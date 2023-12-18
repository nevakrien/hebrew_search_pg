import psycopg2
from setup import conn_params

import numpy as np

def convert_embedding_str_to_array(embedding_str):
    # Remove the curly braces and convert to numpy array
    return np.fromstring(embedding_str[1:-1], sep=',')

def knn_query_postgresql(conn, query_embedding, subset_limit=1000, k=5):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, embedding
            FROM (
                SELECT id, embedding
                FROM snippets
                WHERE embedding IS NOT NULL
                ORDER BY id
                LIMIT %s
            ) AS limited_set
            ORDER BY limited_set.embedding <-> %s
            LIMIT %s;
        """, (subset_limit, query_embedding, k))
        return cursor.fetchall()


def fetch_sample_embedding(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT embedding
            FROM snippets
            WHERE embedding IS NOT NULL
            LIMIT 1;
        """)
        return cursor.fetchone()[0]

def fetch_embeddings(conn, limit=1000):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, embedding
            FROM snippets
            WHERE embedding IS NOT NULL 
            ORDER BY id
            LIMIT %s;
        """, (limit,))
        return cursor.fetchall()




def euclidean_distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))

def manual_knn(query_embedding, embeddings, k=5):
    l=((embeddings-query_embedding)**2).sum(1)
    #print(l.shape)
    return embeddings[np.argsort(l)[:5]]


if __name__ == "__main__":
    with psycopg2.connect(**conn_params) as conn:
        # Fetch sample embedding and convert to numpy array
        sample_embedding_str = fetch_sample_embedding(conn)
        sample_embedding = convert_embedding_str_to_array(sample_embedding_str)
        print(f'sample embedding: length({len(sample_embedding)}) type({type(sample_embedding)})')#\n{sample_embedding}')

        # Perform kNN in PostgreSQL
        pg_knn_results = knn_query_postgresql(conn, sample_embedding_str)
        pg_knn_results=np.stack([convert_embedding_str_to_array(s[1]) for s in pg_knn_results],0)

        # Fetch limited embeddings for manual kNN and convert to numpy arrays
        embeddings_str = fetch_embeddings(conn)
        embeddings = [(convert_embedding_str_to_array(emb[1])) for emb in embeddings_str]
        embeddings=np.stack(embeddings,0)
        print("embeddings:",embeddings.shape)

        # Manual kNN calculation
        manual_knn_results = manual_knn(sample_embedding, embeddings)

        # Compare results
        print("PostgreSQL kNN Results:", pg_knn_results.shape)
        print("Manual kNN Results:", manual_knn_results.shape)
        
        corect=np.all(pg_knn_results==manual_knn_results)
        if corect:
            print('PostgreSQL==Manual')
        else:
            print('PostgreSQL!=Manual')

        
        print("PostgreSQL error from true",((pg_knn_results-sample_embedding)**2).mean(1))
        print("Manual error from true",((manual_knn_results-sample_embedding)**2).mean(1))