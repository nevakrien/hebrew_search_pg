import torch
from transformers import AutoTokenizer, BertModel
import psycopg2
from setup import conn_params,MAX_CONTEXT,MODEL_NAME


tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME)
model=BertModel.from_pretrained(MODEL_NAME)

def knn_query_postgresql(query_embedding, k=5):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id,token_ids,embedding
                FROM snippets
                ORDER BY embedding <-> %s
                LIMIT %s;
            """, ( str(query_embedding), k))
            return cursor.fetchall()

@torch.no_grad
def get_embeddings(text):
    inputs=tokenizer(text,return_tensors='pt',truncation=True,max_length=MAX_CONTEXT)
    inputs={k:v.to(model.device) for k,v in inputs.items()}
    return model(**inputs).last_hidden_state.mean([1])[0].cpu().tolist()


def get_texts(text,k=5):
	v=get_embeddings(text)
	ans=knn_query_postgresql(v,k)
	return [tokenizer.decode(x[1], skip_special_tokens=True) for x in ans]