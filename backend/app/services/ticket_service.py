# app/services/ticket_service.py

from datetime import datetime
from typing import Optional, Dict, Any

from app.infrastructure.mongo import tickets_col, call_logs_col


def create_ticket_for_call(
    company_id: str,
    call_log_id,
    *,
    customer_name: Optional[str] = None,
    service: Optional[str] = None,
    slot_raw: Optional[str] = None,
) -> str:
    """
    Create a simple ticket linked to a call_log.
    现在先用非常简单的结构，后面再扩展字段就行。
    """

    doc: Dict[str, Any] = {
        "company_id": company_id,
        "call_log_id": call_log_id,
        "customer": {
            "name": customer_name,
        },
        "service": service,           # 暂时只存名字，比如 "plumber"
        "slot_raw": slot_raw,         # 先存原始字符串，后面再解析成 datetime
        "status": "open",             # open | confirmed | closed ...
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = tickets_col().insert_one(doc)
    ticket_id = result.inserted_id

    # 反写回 call_logs，建立关联
    call_logs_col().update_one(
        {"_id": call_log_id},
        {"$set": {"ticket_id": ticket_id}},
    )

    return str(ticket_id)
