# app/api/chat.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from openai import OpenAI

from app.ai.rag import search_kb  # 你现有的 RAG 函数

client = OpenAI()

router = APIRouter(prefix="/ai", tags=["ai"])


# ==============================
# Pydantic Models
# ==============================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    callSid: Optional[str] = Field(None, description="Twilio CallSid")
    companyId: Optional[str] = Field(None, description="Company ID")


class AnswerSource(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    replyText: str
    timestamp: str
    duration: int
    sources: List[AnswerSource]


# ==============================
# /ai/chat 统一 AI 对话入口
# ==============================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    统一 AI 对话端点：
    - 使用 RAG（从 kb_chunks 检索）
    - LLM 生成一个自然语言回答
    - 返回给 Telephony / 前端
    """

    company_id = request.companyId or "demo-company"
    user_msg = request.message.strip()

    # -------- 1) RAG 搜索知识库 --------
    hits = search_kb(
        company_id=company_id,
        question=user_msg,
        top_k=5
    )

    # 拼接 RAG 文本
    context = "\n\n---\n\n".join(h["text"] for h in hits)

    # -------- 2) Prompt --------
    prompt = f"""
You are the AI phone assistant for company: {company_id}.

### Knowledge Base:
{context or "NO KNOWLEDGE FOUND"}

### User Message:
{user_msg}

### Instruction:

- If the user message is about booking, scheduling, reserving, or making an appointment or meeting:
  - help gather the needed details step by step
  - ask for missing information such as date, time, and name
  - keep the reply short and suitable for phone conversation

- Otherwise, if the answer exists in the knowledge base, use it.

- If the answer cannot be found and it is not a booking request, say:
  "I'm not sure about that, but I can help with booking or general questions."

- Keep the response short and suitable for phone conversation.
    """
# - If the answer exists in the knowledge base, use it.
# - If the user wants to make a booking, appointment, or meeting:
#   - help gather the needed details step by step
#   - ask for missing information such as date, time, and name
#   - keep the reply short and suitable for phone conversation
# - If the answer cannot be found and it is not a booking request, say:
#   "I'm not sure about that, but I can help with booking or general questions."
# - Keep the response short and suitable for phone conversation.
#     """

    # -------- 3) OpenAI 回复 --------
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    reply = resp.choices[0].message.content or "Sorry, something went wrong."

    # -------- 4) 返回 --------
    return ChatResponse(
        replyText=reply,
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration=len(reply),
        sources=hits,
    )



# from fastapi import APIRouter
# from datetime import datetime
# from pydantic import BaseModel

# router = APIRouter(prefix="/ai", tags=["chat"])


# class ChatRequest(BaseModel):
#     message: str


# class ChatResponse(BaseModel):
#     replyText: str
#     timestamp: str
#     duration: int


# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     """Stubbed chat endpoint - returns success response"""
#     return ChatResponse(
#         replyText="I'm currently being updated. Please try again later.",
#         timestamp=datetime.now().isoformat(),
#         duration=50,
#     )
