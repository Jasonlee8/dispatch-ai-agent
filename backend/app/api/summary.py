from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI

client = OpenAI()

router = APIRouter(prefix="/ai", tags=["ai-summary"])


class ConversationMessage(BaseModel):
    speaker: str
    message: str
    timestamp: str


class SummaryRequest(BaseModel):
    callSid: str
    conversation: List[ConversationMessage]
    serviceInfo: Dict[str, Any]


class SummaryResponse(BaseModel):
    summary: str
    keyPoints: List[str]


@router.post("/summary", response_model=SummaryResponse)
async def generate_ai_summary(req: SummaryRequest):

    conversation_text = "\n".join(
        [f"{m.speaker}: {m.message}" for m in req.conversation]
    )

    prompt = f"""
You are an AI assistant that summarises phone calls for a service business.

Conversation:
{conversation_text}

Service Info:
{req.serviceInfo}

Generate:
1) A helpful summary of what happened  
2) 3–5 key points
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    text = resp.choices[0].message.content.strip()

    # simple extraction (可 later 用正则优化)
    if "Key Points:" in text:
        summary, keys = text.split("Key Points:")
        key_points = [k.strip("- •\n ") for k in keys.split("\n") if k.strip()]
    else:
        summary = text
        key_points = []

    return SummaryResponse(summary=summary.strip(), keyPoints=key_points)



# from fastapi import APIRouter
# from pydantic import BaseModel
# from typing import List, Dict, Any

# router = APIRouter(prefix="/ai", tags=["ai-summary"])


# class ConversationMessage(BaseModel):
#     speaker: str
#     message: str
#     timestamp: str


# class SummaryRequest(BaseModel):
#     callSid: str
#     conversation: List[ConversationMessage]
#     serviceInfo: Dict[str, Any]


# class SummaryResponse(BaseModel):
#     summary: str
#     keyPoints: List[str]


# @router.post("/summary", response_model=SummaryResponse)
# async def generate_ai_summary(request: SummaryRequest):
#     """Stubbed summary endpoint - returns basic response"""
#     return SummaryResponse(
#         summary="Summary generation is temporarily unavailable.",
#         keyPoints=["Service is being updated"]
#     )
