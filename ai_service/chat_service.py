from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = f"""
You are Maya, a personal jewelry stylist at {os.getenv('STORE_NAME', 'our jewelry store')}.
{os.getenv('STORE_DESCRIPTION', 'We sell beautiful handcrafted jewelry including necklaces, rings, bracelets and earrings.')}
Your tone is warm, elegant, and knowledgeable — like a trusted friend who knows jewelry.

Rules you must ALWAYS follow:
- Always ask about the customer's budget before recommending products.
- Never recommend a product we don't carry (necklaces, rings, bracelets, earrings).
- Always end your reply with exactly one follow-up question.
- Keep answers to 3-4 sentences maximum.
- If the user mentions another store or competitor, say you only know our collection.
- If asked about sizing, mention we offer multiple sizes and suggest visiting the store to try on.

When comparing two products, use this exact structure:
Option A: [name] - [one sentence benefit]
Option B: [name] - [one sentence benefit]
My pick: [which one and why, one sentence]

Example:
User: I'm looking for a gift for my mom.
Maya: How lovely! I'd be happy to help you find something special for her.
To point you to the best pieces, could I ask what your budget range is?

User: Around $100, she loves classic styles.
Maya: Perfect, $100 gives us beautiful options! For a classic look, I'd suggest a pearl necklace or a delicate gold bracelet — both are timeless and elegant.
Does your mom prefer gold or silver tones?
"""

# ── PRODUCT EMBEDDINGS CACHE ─────────────────────────────────
product_embeddings_cache: list[dict] = []

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def find_top_products(query: str, top_k: int = 5) -> list:
    if not product_embeddings_cache:
        return []
    query_embedding = get_embedding(query)
    scored = []
    for item in product_embeddings_cache:
        score = cosine_similarity(query_embedding, item['embedding'])
        scored.append({**item['product'], 'score': round(score, 3)})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]

# ── DATA MODELS ──────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []
    products: list = []

class SearchRequest(BaseModel):
    query: str
    products: list = []
    top_k: int = 5

# ── STARTUP: PRE-COMPUTE EMBEDDINGS ──────────────────────────
class InitRequest(BaseModel):
    products: list

@app.post('/init')
async def init_embeddings(req: InitRequest):
    global product_embeddings_cache
    product_embeddings_cache = []
    for p in req.products:
        text = f"{p.get('name', '')} {p.get('description', '')} {p.get('color', '')}"
        embedding = get_embedding(text)
        product_embeddings_cache.append({'product': p, 'embedding': embedding})
    return {'initialized': len(product_embeddings_cache)}

# ── SEARCH ENDPOINT ──────────────────────────────────────────
@app.post('/search')
async def search(req: SearchRequest):
    if not req.products:
        return {'results': []}
    # Use cache if available, otherwise compute on the fly
    if product_embeddings_cache:
        results = find_top_products(req.query, req.top_k)
    else:
        query_embedding = get_embedding(req.query)
        scored = []
        for p in req.products:
            text = f"{p.get('name', '')} {p.get('description', '')} {p.get('color', '')}"
            product_embedding = get_embedding(text)
            score = cosine_similarity(query_embedding, product_embedding)
            scored.append({**p, 'score': round(score, 3)})
        scored.sort(key=lambda x: x['score'], reverse=True)
        results = scored[:req.top_k]
    return {'results': results}

# ── CHAT ENDPOINT ────────────────────────────────────────────
@app.post('/chat')
async def chat(req: ChatRequest):
    # Use semantic search to find top 5 relevant products
    if req.products:
        top_products = find_top_products(req.message, top_k=5) if product_embeddings_cache \
            else req.products[:5]
        catalog_lines = []
        for p in top_products:
            line = f"- {p.get('name')} (${p.get('price')}) | Color: {p.get('color', '')} | {p.get('description', '')}"
            catalog_lines.append(line)
        catalog = '\n'.join(catalog_lines)
        full_prompt = SYSTEM_PROMPT + f'\n\nMost relevant products:\n{catalog}\n\nOnly recommend products from this list.'
    else:
        full_prompt = SYSTEM_PROMPT

    messages = [{'role': 'system', 'content': full_prompt}]
    for m in req.history:
        messages.append({'role': m.role, 'content': m.content})
    messages.append({'role': 'user', 'content': req.message})

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        max_tokens=400,
        temperature=0.6
    )
    return {'reply': response.choices[0].message.content}
