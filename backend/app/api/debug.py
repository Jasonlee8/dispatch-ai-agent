# app/api/debug.py

from fastapi import APIRouter
from app.services.call_log_service import create_call_log, finalize_call_log
from app.ai.intent import classify_intent
from app.services.ticket_service import create_ticket_for_call
from app.ai.rag import answer_faq


router = APIRouter(prefix="/debug", tags=["Debug / Demo"])


@router.post("/mock_call")
async def mock_call(company_id: str = "demo_company"):
    """
    Simulate an incoming call for demo purposes.
    For now, company_id 只是一个字符串，不用 ObjectId。
    """

    # 1) Demo transcript（你之后可以换成更复杂的）
    transcript = """
    Hi, this is John. I need a plumber tomorrow morning to fix a leaking pipe.
    Do you have availability around 10am?
    """

    # 2) Create a call_log entry（company_id 直接用字符串）
    call_log_id = create_call_log(
        company_id=company_id,
        from_number="+61451234567",
        to_number="+61123456789",
    )

    # 3) AI Intent Classification
    result = classify_intent(transcript)

    # 4) Update call_log
    finalize_call_log(
        call_log_id,
        intent=result.get("intent"),
        priority=result.get("priority", "normal"),
        summary=f"AI summary: {result}",
    )

    ticket_id: str | None = None
    if result.get("intent") == "booking":
        customer_name = result.get("customer", {}).get("name")
        service = result.get("service")
        slot_raw = result.get("slot")  # 现在是 "yyyy-mm-dd 10:00" 之类

        ticket_id = create_ticket_for_call(
            company_id=company_id,
            call_log_id=call_log_id,
            customer_name=customer_name,
            service=service,
            slot_raw=slot_raw,
        )

    return {
        "call_log_id": str(call_log_id),
        "ticket_id": ticket_id,
        "intent": result.get("intent"),
        "priority": result.get("priority"),
        "structured_data": result,
    }


@router.post("/mock_call_faq")
async def mock_call_faq(company_id: str = "demo_company"):
    """
    模拟一通 FAQ 电话：用户问价格 & 营业时间。
    走的是 RAG 流程。
    """

    transcript = """
    Hi, I just want to know your business hours and how much a plumber costs.
    """

    # 1) 建一条 call_log
    call_log_id = create_call_log(
        company_id=company_id,
        from_number="+61450000001",
        to_number="+61123456789",
    )

    # 2) 用 RAG 回答
    rag_result = answer_faq(company_id, transcript)
    answer = rag_result["answer"]

    # 3) 写回 call_log（intent 先直接标为 faq）
    finalize_call_log(
        call_log_id,
        intent="faq",
        priority="normal",
        summary=answer,
    )

    return {
        "call_log_id": str(call_log_id),
        "intent": "faq",
        "answer": answer,
        "rag_sources": rag_result["sources"],
    }
