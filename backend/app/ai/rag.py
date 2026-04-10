# app/ai/rag.py

from typing import List, Tuple, Dict, Any
from math import sqrt

from openai import OpenAI
from fastapi import APIRouter            
from pydantic import BaseModel  
from app.infrastructure.mongo import kb_chunks_col

client = OpenAI()


def _cosine(a: List[float], b: List[float]) -> float:
    """纯 Python 的 cosine，相似度计算。"""
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def embed_text(text: str) -> List[float]:
    """对问题做 embedding。"""
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return resp.data[0].embedding


def search_kb(company_id: str, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    从 kb_chunks 做一个最简单的向量检索。
    现在 demo 数据量不大，直接全量拉出来算 cosine 就够了。
    """
    q_emb = embed_text(question)

    chunks = list(kb_chunks_col().find({"company_id": company_id}))
    if not chunks:
        return []

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for c in chunks:
        emb = c.get("embedding")
        if not emb:
            continue
        score = _cosine(q_emb, emb)
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [c for _, c in scored[:top_k]]
    return top


def answer_faq(company_id: str, question: str) -> Dict[str, Any]:
    """
    用 RAG 回答 FAQ：
    - 检索 top_k chunks
    - 让 LLM 基于这些 chunks 生成答案
    返回 {answer, sources}
    """
    chunks = search_kb(company_id, question, top_k=3)

    if not chunks:
        return {
            "answer": "I couldn't find any information about that in the knowledge base.",
            "sources": [],
        }

    context = "\n\n".join(f"- {c['text']}" for c in chunks)

    prompt = f"""
You are an AI assistant for a small business.

Here is the business knowledge:

{context}

Question from caller:
{question}

Answer briefly and clearly in natural language.
If the answer is not in the knowledge, say you don't know.
"""

    chat = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = chat.choices[0].message.content.strip()

    return {
        "answer": answer,
        "sources": [
            {"id": str(c["_id"]), "text": c["text"], "tags": c.get("tags", [])}
            for c in chunks
        ],
    }


router = APIRouter(prefix="/rag", tags=["rag"])


class RagRequest(BaseModel):
    question: str
    company_id: str | None = None


@router.post("/ask")
async def rag_ask(payload: RagRequest):
    company_id = payload.company_id or "demo_company"
    return answer_faq(company_id, payload.question)







## Gemini FileSearch