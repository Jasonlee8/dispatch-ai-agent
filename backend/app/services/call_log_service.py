# app/services/call_log_service.py

from datetime import datetime
from typing import Optional, Dict, Any

from app.infrastructure.mongo import call_logs_col


def create_call_log(
    company_id: str,
    from_number: str,
    to_number: str,
    start_time: Optional[datetime] = None,
):
    """
    Create a new call_log document and return its Mongo _id.
    For now company_id 用字符串就好（例如 'demo_company'）。
    """
    doc = {
        "company_id": company_id,
        "from_number": from_number,
        "to_number": to_number,
        "start_time": start_time or datetime.utcnow(),
        "end_time": None,
        "status": "ongoing",      # ongoing | completed | failed
        "priority": "normal",     # normal | high | emergency
        "intent": None,           # booking | faq | emergency ...
        "transcript": "",
        "summary": "",
        "ticket_id": None,
        "extra": {},
        "created_at": datetime.utcnow(),
    }
    result = call_logs_col().insert_one(doc)
    return result.inserted_id


def finalize_call_log(
    call_log_id,
    *,
    end_time: Optional[datetime] = None,
    status: str = "completed",
    intent: Optional[str] = None,
    priority: Optional[str] = None,
    summary: Optional[str] = None,
):
    """
    Update a call_log when the call is finished / AI has classified it.
    """
    update: Dict[str, Any] = {
        "end_time": end_time or datetime.utcnow(),
        "status": status,
    }

    if intent is not None:
        update["intent"] = intent

    if priority is not None:
        update["priority"] = priority

    if summary is not None:
        update["summary"] = summary

    call_logs_col().update_one({"_id": call_log_id}, {"$set": update})
