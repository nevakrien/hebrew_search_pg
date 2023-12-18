import psycopg2
from setup import conn_params,MAX_CONTEXT,MODEL_NAME

from tqdm import tqdm
import torch
from transformers import AutoModel

def fetch_snippets_without_embeddings(conn, limit=100):
    """Fetch snippets from the database that don't have embeddings."""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, token_ids
            FROM snippets
            WHERE embedding IS NULL AND token_ids IS NOT NULL
            LIMIT %s;
        """, (limit,))
        return cursor.fetchall()

def count_snippets_without_embeddings(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM snippets
            WHERE embedding IS NULL AND token_ids IS NOT NULL;
        """)
        count = cursor.fetchone()[0]
    return count

def process_batch_and_update_embeddings(batch, conn,model,device):
    """Process a batch of snippets to generate and update embeddings."""
    # Prepare the batch for processing
    tokens=[row[1] for row in batch]
    attention_mask=torch.IntTensor([[1]*len(t)+[0]*(MAX_CONTEXT-len(t)) for t in tokens]).to(device)
    input_ids = torch.IntTensor([t+[0]*(MAX_CONTEXT-len(t)) for t in tokens]).to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        mask = attention_mask[:, :, None]
        outputs *= mask
        embeddings = (outputs.sum(1) / mask.sum(1)).cpu().numpy()

    #print(embeddings.shape)
    # Update the database
    for snippet, embedding in zip(batch, embeddings):
        update_embedding(conn, snippet[0], embedding)

def update_embedding(conn, snippet_id, embedding):
    #print(embedding.shape)
    """Update a single snippet's embedding in the database."""
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE snippets
            SET embedding = %s
            WHERE id = %s;
        """, (embedding.tolist(), snippet_id))
    conn.commit()


def process_embeddings(batch_size=500,cup=None):
    # Load the model
    print("loading model pytorch may raise a warning")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoModel.from_pretrained(MODEL_NAME).to(device)

    with psycopg2.connect(**conn_params) as conn:
        total=count_snippets_without_embeddings(conn)
        print(f"found {total} snippets in need of embeddings")
        bar=tqdm(total=total)
        batch = fetch_snippets_without_embeddings(conn, limit=batch_size)
        while(batch):
            process_batch_and_update_embeddings(batch, conn,model,device)
            batch = fetch_snippets_without_embeddings(conn, limit=batch_size)
            bar.update(len(batch))
            if(cup is not None and bar.n>=cup):
                print('early break (this is used for testing)')
                break

if __name__ == "__main__":
    process_embeddings()#cup=1000)
