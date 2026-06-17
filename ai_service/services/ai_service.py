from openai import OpenAI
from core.config import OPENAI_API_KEY, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def build_prompt(products: list) -> str:
    if not products:
        return SYSTEM_PROMPT
    catalog = '\n'.join(
        f"- {p.get('name')} (${p.get('price')}) | Color: {p.get('color', '')} | {p.get('description', '')}"
        for p in products
    )
    return SYSTEM_PROMPT + f'\n\nMost relevant products:\n{catalog}\n\nOnly recommend products from this list.'

def get_chat_reply(message: str, history: list, products: list) -> str:
    messages = [{'role': 'system', 'content': build_prompt(products)}]
    messages += [{'role': m.role, 'content': m.content} for m in history]
    messages.append({'role': 'user', 'content': message})

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        max_tokens=400,
        temperature=0.6
    )
    return response.choices[0].message.content
