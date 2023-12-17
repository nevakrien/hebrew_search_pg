import psycopg2
from setup import conn_params
import datasets
from tqdm import tqdm
import re 

import io

def length(s):
    if not s:
        return 0
    s=" ".join(s.split('\n'))
    return len(s.split(' '))

def document_iter(text_list):
    bads = (
            re.compile(r'<!--\s*\n\s*/\*\s*Font Definitions\s*\*/'),
            re.compile(r'\uFFFD'),
            re.compile(r'endstream.*?(?=\n|$)'),
            re.compile(r'/Author \(user\)\n|/Creator'),
            re.compile(r'\ue51d'),
            re.compile(r'[\u0080-\u00FF\u0100-\u017F]'), #weird latin dialects like ã
           )
            

    
    for text in text_list:
        if not text:
            continue
        text=text.strip()
        
        if text in ("File not found",""):
            continue
            
        skip=False
        for b in bads:
            if b.search(text):
                skip=True
                break
        if skip:
            continue

        yield (re.sub(r'\n\s*\n\s*\n+', '\n\n', text),None)
        

def create_in_memory_csv(documents):
    # Create an in-memory bytes buffer
    csv_buffer = io.BytesIO()

    # Write data to the buffer
    for doc in documents:
        snippet = ','.join(['"' + str(field).replace('"', '""') + '"' for field in doc]) + '\n'
        csv_buffer.write(snippet.encode('utf-8'))

    # Reset buffer position to the beginning
    csv_buffer.seek(0)
    return csv_buffer

def bulk_move(csv_buffer):
    # Connect to the database
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.copy_expert("COPY documents (text, path) FROM STDIN WITH CSV", csv_buffer)

if __name__ == "__main__":
    data = datasets.load_dataset('LevMuchnik/SupremeCourtOfIsrael')
    texts = data['train']['text']

    csv_buffer = create_in_memory_csv(document_iter(tqdm(texts)))
    print('moving from memory to disk this may take a while...')
    bulk_move(csv_buffer)
    print('done')
