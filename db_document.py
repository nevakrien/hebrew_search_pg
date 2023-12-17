import psycopg2
from setup import conn_params
import datasets
from tqdm import tqdm
import re 

import os
import contextlib
import mmap

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
        

def create_memory_mapped_file(documents):
    # Create a temporary file
    temp_file_path = 'temp_data.csv'
    with open(temp_file_path, 'w+', encoding='utf-8') as temp_file:
        # Go through the documents and write to the temp file
        for doc in documents:
            temp_file.write(','.join(['"' + str(field).replace('"', '""') + '"' for field in doc]) + '\n')
        
        # Memory-map the file
        temp_file.flush()
        with contextlib.closing(mmap.mmap(temp_file.fileno(), 0, access=mmap.ACCESS_READ)) as m:
            yield temp_file_path, m

def bulk_move(file_path, mem_map):
    # Connect to the database
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.copy_expert(f"COPY documents (text, path) FROM STDIN WITH CSV", mem_map)

    # Clean up the temporary file
    os.remove(file_path)


if __name__=="__main__":
    data = datasets.load_dataset('LevMuchnik/SupremeCourtOfIsrael')
    texts=data['train']['text']

    for file_path, mem_map in create_memory_mapped_file(document_iter(tqdm(texts))):
        print('moving from memory to disk this may take a while...')
        bulk_move(file_path, mem_map)
    print('done')
