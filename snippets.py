import psycopg2
from setup import conn_params,MAX_CONTEXT,MODEL_NAME

import concurrent
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import io
from tqdm import tqdm

def get_strategy_id(strategy_name):
    """Ensures that a generation strategy exists in the database, adds it if not, and returns its ID."""
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM generation_strategies WHERE name = %s", (strategy_name,))
            result = cursor.fetchone()
            if result is None:
                # Strategy not found, insert it
                cursor.execute("INSERT INTO generation_strategies (name) VALUES (%s) RETURNING id", (strategy_name,))
                strategy_id = cursor.fetchone()[0]
                print(f"Added new generation strategy '{strategy_name}' with ID {strategy_id}")
                return strategy_id
            else:
                print(f"Generation strategy '{strategy_name}' already exists")
                return result[0]

def get_total_document_count(sql_query="SELECT id, text FROM documents"):
    """Get the total count of documents based on the provided SQL query."""
    count_query = f"SELECT COUNT(*) FROM ({sql_query}) as subquery"
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(count_query)
            return cursor.fetchone()[0]

def fetch_documents(offset, limit,conn, sql_query="SELECT id, text FROM documents"):
    """Fetch a batch of documents based on the provided SQL query."""
    query = f"{sql_query} LIMIT %s OFFSET %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (limit, offset))
        return cursor.fetchall()


def document_batches(batch_size, sql_query,total=None):
    """Yield batches of documents from the database based on the SQL query."""
    if total!=None:
        bar = tqdm(total=total)
        
    offset = 0
    with psycopg2.connect(**conn_params) as conn:
        while True:
            documents = fetch_documents(offset, batch_size,conn, sql_query)
            if not documents:
                break
            yield documents
            offset += len(documents)
            if total!=None:
                bar.update(len(documents))


def mass_snippets(process_function, strategy_name, batch_size=1000, sql_query="SELECT id, text FROM documents"):
    strategy_id = get_strategy_id(strategy_name)
    total_documents = get_total_document_count(sql_query)

    batches = document_batches(batch_size, sql_query,total_documents)
    with psycopg2.connect(**conn_params) as conn:
        with ThreadPoolExecutor(cpu_count() - 1) as executor:
            # First map: Over each batch
            for batch in batches:
                process_batch(batch, process_function, strategy_id, executor,conn)
            
        conn.commit()

    print('Processing complete.')

def process_batch(batch, process_function, strategy_id, executor,conn):
    # Second map: Over each document in the batch 
    batch_futures = [executor.submit(process_and_move, doc, process_function, strategy_id,conn) for doc in batch]
    for future in concurrent.futures.as_completed(batch_futures):
        future.result()  # Wait for each document to complete

def process_and_move(document, process_function, strategy_id, conn):
    """Process a single document and insert snippets directly into the database."""
    for snippet in process_function(document[1]):
        # Ensure that the tuple (document[0], strategy_id) + snippet has the correct number of elements
        insert_values = (document[0], strategy_id) + snippet
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO snippets (document_id, generation_strategy_id, text, token_ids, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, insert_values)
       # conn.commit()  # Commit after each insert. Adjust as needed for performance.


def naive_chunking(text,tokenizer,max=MAX_CONTEXT):
    tokens=tokenizer.encode(text)
    for i in range(0,len(tokens),MAX_CONTEXT):
        yield (None,tokens[i:i+MAX_CONTEXT],None)

if __name__ == "__main__":
    from transformers import AutoTokenizer
    import os
    tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME)
    os.environ["TOKENIZERS_PARALLELISM"]='false'

    mass_snippets(lambda t: naive_chunking(t,tokenizer),"naive_chunking")
