from fastapi import APIRouter
from models.schemas import ChatRequest, SearchRequest, InitRequest
from services import search_service
from services.ai_service import get_chat_reply
from services.search_service import get_embedding, cosine_similarity, find_top_products, init_cache

router = APIRouter()

@router.post('/init')
async def init_embeddings(req: InitRequest):
    count = init_cache(req.products)
    return {'initialized': count}

@router.post('/search')
async def search(req: SearchRequest):
    if not req.products:
        return {'results': []}
    if search_service.product_embeddings_cache:
        return {'results': find_top_products(req.query, req.top_k)}
    query_embedding = get_embedding(req.query)
    scored = []
    for p in req.products:
        text = f"{p.get('name', '')} {p.get('description', '')} {p.get('color', '')}"
        score = cosine_similarity(query_embedding, get_embedding(text))
        scored.append({**p, 'score': round(score, 3)})
    return {'results': sorted(scored, key=lambda x: x['score'], reverse=True)[:req.top_k]}

@router.post('/chat')
async def chat(req: ChatRequest):
    top_products = find_top_products(req.message, top_k=5) if search_service.product_embeddings_cache \
        else req.products[:5]
    reply = get_chat_reply(req.message, req.history, top_products)
    return {'reply': reply}
