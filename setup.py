import psycopg2

# Database connection parameters
conn_params = {
    'dbname': 'hebrew_document_search',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

# Embedding size parameter
EMBEDDING_SIZE = 768

def initdb():
    with open('setup.sql', 'r') as file:
        sql_script = file.read()
    # Connect to the database
    with psycopg2.connect(**conn_params) as conn:
        # Create custom type for embeddings
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE EXTENSION vector")
            cursor.execute(f"CREATE DOMAIN embedding_type AS VECTOR({EMBEDDING_SIZE});")
            cursor.execute(sql_script)

if __name__ == "__main__":
    initdb()
