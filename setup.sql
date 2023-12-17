--CREATE EXTENSION vector;

--CREATE DOMAIN embedding_type AS VECTOR(768); -- setup correct size for us its this

-- Create the Generation Strategies Table
CREATE TABLE generation_strategies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Create the Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    text TEXT,
    path TEXT

);

-- Create the Snippets Table
CREATE TABLE snippets (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    generation_strategy_id INT NOT NULL,

    text TEXT,
    token_ids INT[],
    embedding embedding_type, 

    FOREIGN KEY (generation_strategy_id) REFERENCES generation_strategies (id),
    FOREIGN KEY (document_id) REFERENCES documents (id)
);

CREATE INDEX idx_generation_strategy ON snippets (generation_strategy_id);
