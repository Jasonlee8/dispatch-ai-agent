# app/api/call.py

from datetime import datetime, timezone
from typing import Dict, Any, Literal
import os

import httpx  # 需要在你的 AI 服务环境里安装：pip install httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)

AUTH_LOGIN_URL = os.getenv(
    "AUTH_LOGIN_URL",
    "http://localhost:4000/api/auth/login"
)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "john.doe@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")

# ========= 配置区：Booking API & 默认 IDs =========

BOOKING_API_URL = os.getenv(
    "BOOKING_API_URL",
    "http://localhost:4000/api/bookings",  # 视你的 Nest/Next 反向代理而定
)

DEFAULT_SERVICE_ID = os.getenv("DEFAULT_SERVICE_ID", "SERVICE_ID_FOR_DEMO")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "USER_ID_FOR_DEMO")
DEFAULT_SERVICE_FIELD_ID = os.getenv("DEFAULT_SERVICE_FIELD_ID", "notes-field")


# ========= 会话状态（临时：内存里；以后可以换 Redis） =========

Step = Literal[
    "ask_name",
    "ask_phone",
    "ask_address",
    "ask_service",
    "ask_time",
    "confirm",
    "done",
]

# 内存中的简单 session 存储：只用于演示
CALL_SESSIONS: Dict[str, Dict[str, Any]] = {}

# def _get_service_token() -> str | None:
#     """
#     调用 Nest 的登录接口，获取一个 JWT，用来调用 /bookings。
#     Demo 阶段简单点：每次创建 booking 就登录一次。
#     """
#     try:
#         resp = httpx.post(
#             AUTH_LOGIN_URL,
#             json={
#                 "email": AUTH_EMAIL,      # 根据实际字段名改
#                 "password": AUTH_PASSWORD,
#             },
#             timeout=5.0,
#         )
#         resp.raise_for_status()
#         data = resp.json()

#         # 根据 Nest 返回结构拿 token
#         token = (
#             data.get("accessToken")
#             or data.get("token")
#             or data.get("jwt")
#         )
#         if not token:
#             print("❌ Login ok but no token field in response:", data)
#             return None

#         print("✅ Got service token from auth")
#         return token

#     except Exception as e:
#         print(f"❌ Failed to get service token: {e}")
#         return None

def _get_service_token() -> str | None:
    """
    登录 NestJS，获得 JWT token。
    """
    try:
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        resp = httpx.post(AUTH_LOGIN_URL, json=payload, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()

        # Nest login 返回的 token 字段可能是 accessToken 或 token
        token = data.get("access_token") or data.get("token")

        if token:
            print("✅ Got service token from NestJS")
            return token

        print("❌ Login succeeded but no token in response:", data)
        return None

    except Exception as e:
        print(f"❌ Failed to get service token: {e}")
        return None



def _init_session(call_sid: str) -> Dict[str, Any]:
    """创建或获取一个 session"""
    if call_sid not in CALL_SESSIONS:
        CALL_SESSIONS[call_sid] = {
            "current_step": "ask_name",
            "booking": {
                "customerName": None,
                "phoneNumber": None,
                "address": None,
                "serviceName": None,
                "bookingTime": None,
                "bookingId": None,  # Nest 返回的 _id 可以存这里（可选）
            },
            "history": [],
            "createdAt": datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            ),
        }
    return CALL_SESSIONS[call_sid]


def _build_summary(booking: Dict[str, Any]) -> str:
    """生成最终 summary 文本（可以以后用 GPT 来润色）"""
    return (
        "Let me repeat your booking details. "
        f"Name: {booking.get('customerName')}. "
        f"Phone: {booking.get('phoneNumber')}. "
        f"Address: {booking.get('address')}. "
        f"Service: {booking.get('serviceName')}. "
        f"Preferred time: {booking.get('bookingTime')}. "
        "If everything is correct, we will process your booking shortly."
    )


def _create_booking_for_call(call_sid: str, booking: Dict[str, Any]) -> None:
    """
    在 Nest 后端创建一条 ServiceBooking。
    注意：Nest 的 /bookings 路由有 JWT 守卫的话，需要你那边改成允许内部调用，
    或者在这里加上一个固定的 Bearer token。
    """

    # bookingTime 这里为了简单，直接用“现在时间”，
    # 真正要解析用户说的时间可以后面再加（用 dateparser 等）
    booking_time_iso = datetime.now(timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )

    payload = {
        "serviceId": DEFAULT_SERVICE_ID,
        "client": {
            "name": booking.get("customerName") or "Unknown",
            "phoneNumber": booking.get("phoneNumber") or "",
            "address": booking.get("address") or "",
        },
        # 简化版：用一个 notes 字段把其它内容塞进去
        "serviceFormValues": [
            {
                "serviceFieldId": DEFAULT_SERVICE_FIELD_ID,
                "answer": (
                    f"Service: {booking.get('serviceName')}; "
                    f"Preferred time: {booking.get('bookingTime')}"
                ),
            }
        ],
        "bookingTime": booking_time_iso,
        "status": "Confirmed",
        "note": f"Created by AI phone agent for call {call_sid}",
        "userId": DEFAULT_USER_ID,
        "callSid": call_sid,
    }

    try:
        headers = {
            "Content-Type": "application/json"
            # 如果 /bookings 需要 JWT，这里加：
            # "Authorization": f"Bearer {os.getenv('BOOKING_SERVICE_TOKEN')}"
        }

        resp = httpx.post(
            BOOKING_API_URL, json=payload, headers=headers, timeout=5.0
        )
        resp.raise_for_status()
        data = resp.json()
        booking_id = data.get("_id") or data.get("id")
        if booking_id:
            booking["bookingId"] = booking_id
        print(f"✅ Created booking for call {call_sid}: {booking_id}")
    except Exception as e:
        # Demo 项目，失败了也不要打断通话，只打印 log 即可
        print(f"❌ Failed to create booking for call {call_sid}: {e}")


# ========= Pydantic models =========


class Message(BaseModel):
    speaker: str
    message: str
    startedAt: str


class ConversationInput(BaseModel):
    callSid: str = Field(..., description="Twilio CallSid – unique call ID")
    customerMessage: Message = Field(
        ..., description="Customer message object"
    )


class ReplyInput(BaseModel):
    callSid: str = Field(..., description="Twilio CallSid – unique call ID")
    message: str = Field(..., description="User message text")


class ReplyOutput(BaseModel):
    replyText: str
    shouldHangup: bool = False         
    step: Step
    booking: Dict[str, Any]
    bookingId: str | None = None  


# ========= 核心逻辑：一步步填 booking，并在合适时机创建后端 Booking =========


def _handle_step(call_sid: str, user_text: str) -> ReplyOutput:
    session = _init_session(call_sid)
    step: Step = session["current_step"]
    booking = session["booking"]

    # 记录历史（optional）
    session["history"].append(
        {
            "speaker": "customer",
            "message": user_text,
            "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    )

    text = user_text.strip().lower()

    if step == "confirm":
        if text in ["yes", "yeah", "yep", "correct", "confirm", "ok", "okay", "sure"]:
            # 真正创建 booking
            _create_booking_for_call(call_sid, booking)
            session["current_step"] = "done"

            return ReplyOutput(
                replyText=f"Great! Your booking ID is {booking.get('bookingId')}. Goodbye!",
                step="done",
                booking=booking,
                shouldHangup=True,
                bookingId=booking.get("bookingId"),
            )

        if text in ["no", "nah", "nope", "wrong"]:
            session["current_step"] = "ask_name"

            session["booking"] = {
                "customerName": None,
                "phoneNumber": None,
                "address": None,
                "serviceName": None,
                "bookingTime": None,
                "bookingId": None,
            }
            return ReplyOutput(
                replyText="No problem. Let's redo your booking. What is your name?",
                step="ask_name",
                booking=booking,
                shouldHangup=False,
                bookingId=booking.get("bookingId"),            
            )

        return ReplyOutput(
            replyText="Please say YES or NO.",
            step="confirm",
            booking=booking,
            shouldHangup=False,
            bookingId=booking.get("bookingId"),
        )


    # 根据当前 step，将用户的这句话写入对应字段，然后切到下一个 step
    if step == "ask_name":
        booking["customerName"] = user_text.strip()
        session["current_step"] = "ask_phone"
        reply = f"Thanks {booking['customerName']}. May I have your phone number?"

    elif step == "ask_phone":
        booking["phoneNumber"] = user_text.strip()
        session["current_step"] = "ask_address"
        reply = "Got it. Could you please tell me your full address?"

    elif step == "ask_address":
        booking["address"] = user_text.strip()
        session["current_step"] = "ask_service"
        reply = (
            "Thank you. What service do you need today? "
            "For example, house cleaning, garden maintenance, or plumbing service."
        )

    elif step == "ask_service":
        booking["serviceName"] = user_text.strip()
        session["current_step"] = "ask_time"
        reply = (
            "Great. When would you like us to come? "
            "Please tell me your preferred date and time."
        )

    elif step == "ask_time":
        booking["bookingTime"] = user_text.strip()
        session["current_step"] = "confirm"
        # 先创建后端 booking（失败也不会中断对话）
        # _create_booking_for_call(call_sid, booking)
        # 然后给用户读一遍 summary
        summary = _build_summary(booking)
        reply = summary + " 🟩 Please say YES to confirm."

    elif step == "confirm":
        # 这里简单处理：无论用户说什么，都结束
        session["current_step"] = "done"
        reply = "Thank you. Your booking has been recorded. Have a great day!"

    else:  # done
        reply = (
            "Your booking has already been recorded. "
            "If you need changes, please call us again."
        )

    return ReplyOutput(
        replyText=reply, 
        step=session["current_step"], 
        booking=booking, 
        shouldHangup=False, 
        bookingId=booking.get("bookingId")
    )


# ========= API endpoints =========


@router.post("/conversation")
async def ai_conversation(data: ConversationInput):
    """
    可选：如果你以后要做 Web 聊天，可以复用同一套逻辑。
    现在先简单用 _handle_step 跑一遍。
    """
    out = _handle_step(data.callSid, data.customerMessage.message)
    ai_response = {
        "speaker": "AI",
        "message": out.replyText,
        "startedAt": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
    }
    # return {"aiResponse": ai_response, "booking": out.booking, "step": out.step}
    return {
        "aiResponse": ai_response,
        "shouldHangup": out.shouldHangup,
        "extractedInfo": out.booking,
        "step": out.step,
        "bookingId": out.bookingId,
    }


@router.post("/reply", response_model=ReplyOutput)
async def ai_reply(data: ReplyInput):
    """
    Telephony /gather 在每次用户说完话后会调用这个。
    输入：callSid + 用户这句话
    输出：下一句要说什么 + 当前 step + 当前 booking JSON
    """
    out = _handle_step(data.callSid, data.message)
    return out



class StatusInput(BaseModel):
    callSid: str = Field(..., description="Twilio CallSid – unique call ID")


def _forward_status_to_nest(call_sid: str, session: Dict[str, Any]) -> None:
    """
    把最终 summary/booking/history 推送给 Nest 的 /telephony/status
    """
    booking = session["booking"]
    history = session["history"]
    summary = _build_summary(booking)

    payload = {
        "CallSid": call_sid,
        "CallStatus": "completed",
        "finalData": {
            "booking": booking,
            "history": history,
            "summary": summary,
        },
    }

    try:
        resp = httpx.post(
            "http://localhost:4000/api/telephony/status",
            json=payload,
            timeout=5.0,
        )
        resp.raise_for_status()
        print(f"📤 Uploaded finalData to Nest for call {call_sid}")
    except Exception as e:
        print(f"❌ Failed to forward status to Nest: {e}")


@router.post("/status")
async def ai_status(data: StatusInput):
    """
    手动/自动归档接口：
    - 你用 curl 调它
    - 或者以后 Twilio status webhook 结束后由 AI side 调它
    """
    call_sid = data.callSid.strip()
    session = CALL_SESSIONS.get(call_sid)

    if not session:
        return {"success": False, "message": "No session found for this callSid"}

    _forward_status_to_nest(call_sid, session)

    return {
        "success": True,
        "callSid": call_sid,
        "summary": _build_summary(session["booking"]),
        "booking": session["booking"],
        "history": session["history"],
    }




# from fastapi import APIRouter
# from pydantic import BaseModel, Field
# from datetime import datetime, timezone

# router = APIRouter(
#     prefix="/ai",
#     tags=["AI"],
#     responses={404: {"description": "Not found"}},
# )


# # Simple message model
# class Message(BaseModel):
#     speaker: str
#     message: str
#     startedAt: str

# # AI conversation input model
# class ConversationInput(BaseModel):
#     callSid: str = Field(..., description="Twilio CallSid – unique call ID")
#     customerMessage: Message = Field(..., description="Customer message object")


# # Simple reply input model (for telephony service)
# class ReplyInput(BaseModel):
#     callSid: str = Field(..., description="Twilio CallSid – unique call ID")
#     message: str = Field(..., description="User message text")


# @router.post("/conversation")
# async def ai_conversation(data: ConversationInput):
#     """Stubbed AI conversation endpoint - returns success response"""
#     ai_response = {
#         "speaker": "AI",
#         "message": "I'm currently being updated. Please try again later.",
#         "startedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#     }
#     return {"aiResponse": ai_response}


# @router.post("/reply")
# async def ai_reply(data: ReplyInput):
#     """Stubbed AI reply endpoint - returns simple response"""
#     return {"replyText": "I'm currently being updated. Please try again later."}
