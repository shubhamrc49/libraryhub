"""
LLM service - swap provider via LLM_PROVIDER env var.
Supports: mock | ollama | openai
"""
import httpx
from app.core.config import settings


async def _ollama_complete(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["response"]


async def _openai_complete(prompt: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return response.choices[0].message.content


async def llm_complete(prompt: str) -> str:
    if settings.LLM_PROVIDER == "ollama":
        return await _ollama_complete(prompt)
    elif settings.LLM_PROVIDER == "openai":
        return await _openai_complete(prompt)
    else:
        # Mock provider
        if "summary" in prompt.lower():
            return "This is an engaging book that offers valuable insights and a compelling narrative. Readers will find it both informative and enjoyable."
        elif "sentiment" in prompt.lower():
            return "positive"
        elif "recommend" in prompt.lower():
            return "Based on reading history and preferences, these titles offer similar themes, writing styles, and subject matter."
        return "Mock LLM response."


async def generate_book_summary(title: str, author: str, description: str) -> str:
    if not description:
        return f"'{title}' by {author} is a notable work in its genre."
    prompt = f"""Write a concise 2-3 sentence summary of this book:
Title: {title}
Author: {author}
Description: {description}

Summary:"""
    return await llm_complete(prompt)


async def analyze_review_sentiment(review_text: str) -> str:
    if not review_text:
        return "neutral"
    prompt = f"""Analyze the sentiment of this book review. Respond with only one word: positive, negative, or neutral.

Review: {review_text}

Sentiment:"""
    result = await llm_complete(prompt)
    result = result.strip().lower()
    if "positive" in result:
        return "positive"
    elif "negative" in result:
        return "negative"
    return "neutral"


async def generate_review_consensus(reviews: list[dict]) -> str:
    if not reviews:
        return "No reviews yet."
    review_texts = "\n".join([f"Rating: {r['rating']}/5 - {r.get('text', '')}" for r in reviews[:10]])
    prompt = f"""Summarize the overall reader consensus for a book based on these reviews in 2 sentences:

{review_texts}

Consensus:"""
    return await llm_complete(prompt)
