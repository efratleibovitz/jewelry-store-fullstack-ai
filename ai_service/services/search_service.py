import numpy as np
from openai import OpenAI
from core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

product_embeddings_cache: list[dict] = []

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model='text-embedding-3-small', input=text)
    return response.data[0].embedding

def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def build_product_text(p: dict) -> str:
    return f"{p.get('name', '')} {p.get('description', '')} {p.get('color', '')}"

def find_top_products(query: str, top_k: int = 5) -> list:
    if not product_embeddings_cache:
        return []
    query_embedding = get_embedding(query)
    scored = [
        {**item['product'], 'score': round(cosine_similarity(query_embedding, item['embedding']), 3)}
        for item in product_embeddings_cache
    ]
    return sorted(scored, key=lambda x: x['score'], reverse=True)[:top_k]

def init_cache(products: list) -> int:
    global product_embeddings_cache
    product_embeddings_cache = [
        {'product': p, 'embedding': get_embedding(build_product_text(p))}
        for p in products
    ]
    return len(product_embeddings_cache)
