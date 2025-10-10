# AI Service (Python/FastAPI) Specific Rules

Rules specific to the Python AI service in `/backend/ai/`.

## Code Organization

### File Structure

```
ai/
├── app/
│   ├── api/              # FastAPI routers (max 400 lines each)
│   │   ├── call.py
│   │   ├── summary.py
│   │   └── health.py
│   ├── services/         # Business logic (max 500 lines each)
│   │   ├── llm_service.py
│   │   └── conversation_service.py
│   ├── models/           # Pydantic models (max 300 lines each)
│   │   └── schemas.py
│   ├── utils/            # Utilities (max 200 lines each)
│   │   └── helpers.py
│   ├── infrastructure/   # External integrations
│   │   └── redis_client.py
│   ├── config.py         # Configuration
│   └── main.py           # Application entry
└── pyproject.toml
```

## Naming Conventions

### Python Naming (MANDATORY)

```python
# ✅ GOOD - Python conventions

# Constants (UPPER_SNAKE_CASE)
MAX_TOKENS = 2000
API_TIMEOUT = 30
DEFAULT_MODEL = "gpt-4"

# Classes (PascalCase)
class ConversationService:
    pass

class LlmService:
    pass

# Functions/Variables (snake_case)
def process_conversation(message: str) -> str:
    user_input = message.strip()
    return generate_response(user_input)

# Private functions/methods (prefix with _)
def _validate_input(data: dict) -> bool:
    pass

class Service:
    def _internal_method(self):
        pass
```

```python
# ❌ BAD - Wrong conventions

# Don't use camelCase
def processConversation(message):
    userInput = message.strip()

# Don't use lowercase constants
max_tokens = 2000

# Don't omit underscores
class conversationservice:
    pass
```

## Type Hints (MANDATORY)

### ALL Functions Must Have Type Hints

```python
# ✅ GOOD - Type hints everywhere
from typing import List, Dict, Optional

def process_message(
    message: str,
    context: Optional[Dict[str, str]] = None
) -> str:
    """Process a user message and generate a response."""
    if context is None:
        context = {}

    return generate_response(message, context)

async def fetch_conversation_history(
    call_sid: str
) -> List[Dict[str, str]]:
    """Fetch conversation history from Redis."""
    data = await redis_client.get(call_sid)
    return json.loads(data) if data else []

# ❌ BAD - No type hints
def process_message(message, context=None):
    if context is None:
        context = {}
    return generate_response(message, context)
```

### Use Pydantic for Request/Response Models

```python
# ✅ GOOD - Pydantic models
from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    speaker: str = Field(..., description="Who is speaking")
    message: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO timestamp")

class ConversationRequest(BaseModel):
    call_sid: str = Field(..., description="Twilio Call SID")
    customer_message: Message
    context: Optional[Dict[str, str]] = None

class ConversationResponse(BaseModel):
    ai_response: Message
    should_hangup: bool = False

# Router
@router.post("/conversation", response_model=ConversationResponse)
async def process_conversation(request: ConversationRequest):
    # Type-safe and auto-validated
    result = await service.process(request)
    return result
```

## Async/Await (MANDATORY)

### Use async def for I/O Operations

```python
# ✅ GOOD - Async for I/O
import httpx

async def call_openai_api(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={"prompt": prompt}
        )
        return response.json()

async def get_from_redis(key: str) -> Optional[str]:
    return await redis_client.get(key)

# ❌ BAD - Blocking I/O
import requests

def call_openai_api(prompt: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json={"prompt": prompt}
    )
    return response.json()
```

## Error Handling

### Use FastAPI Exception Handling

```python
# ✅ GOOD - Proper error handling
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

async def process_conversation(request: ConversationRequest) -> ConversationResponse:
    try:
        # Validate input
        if not request.call_sid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="call_sid is required"
            )

        # Process
        result = await llm_service.generate_response(request)
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ❌ BAD - Unhandled exceptions
async def process_conversation(request: ConversationRequest):
    result = await llm_service.generate_response(request)
    return result  # What if this fails?
```

## Logging

### Use Python logging Module

```python
# ✅ GOOD - Structured logging
import logging

logger = logging.getLogger(__name__)

async def process_call(call_sid: str, message: str) -> str:
    logger.info(f"Processing call {call_sid}")

    try:
        response = await generate_response(message)
        logger.info(f"Generated response for {call_sid}", extra={
            "call_sid": call_sid,
            "response_length": len(response)
        })
        return response
    except Exception as e:
        logger.error(f"Failed to process call {call_sid}", extra={
            "call_sid": call_sid,
            "error": str(e)
        }, exc_info=True)
        raise

# ❌ BAD - Print statements
def process_call(call_sid: str, message: str) -> str:
    print(f"Processing {call_sid}")  # Don't use print
    response = generate_response(message)
    return response
```

## FastAPI Best Practices

### Router Organization

```python
# ✅ GOOD - Organized router
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ConversationRequest, ConversationResponse
from app.services.conversation_service import ConversationService

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/conversation",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Process conversation",
    description="Process a customer message and generate an AI response",
)
async def process_conversation(
    request: ConversationRequest,
    service: ConversationService = Depends(),
) -> ConversationResponse:
    """
    Process a conversation turn.

    Args:
        request: The conversation request with customer message
        service: Injected conversation service

    Returns:
        AI response with message and hangup decision
    """
    return await service.process(request)
```

### Dependency Injection

```python
# ✅ GOOD - Use FastAPI dependencies
from fastapi import Depends
from app.infrastructure.redis_client import RedisClient

def get_redis() -> RedisClient:
    return RedisClient()

@router.post("/conversation")
async def process_conversation(
    request: ConversationRequest,
    redis: RedisClient = Depends(get_redis),
):
    data = await redis.get(request.call_sid)
    # ...
```

## Code Quality

### Use Ruff for Linting

```bash
# Run ruff
cd backend/ai
ruff check .
ruff format .
```

### Docstrings

```python
# ✅ GOOD - Google-style docstrings
def generate_response(
    prompt: str,
    max_tokens: int = 150,
    temperature: float = 0.7
) -> str:
    """
    Generate an AI response using OpenAI.

    Args:
        prompt: The input prompt for the LLM
        max_tokens: Maximum tokens in response (default: 150)
        temperature: Sampling temperature (default: 0.7)

    Returns:
        The generated text response

    Raises:
        ValueError: If prompt is empty
        HTTPException: If OpenAI API fails

    Example:
        >>> response = generate_response("Hello, how are you?")
        >>> print(response)
        "I'm doing well, thank you!"
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    # Implementation
    pass
```

## Environment Variables

### Use Pydantic Settings

```python
# ✅ GOOD - Pydantic settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "DispatchAI Service"
    api_version: str = "1.0.0"
    debug: bool = False

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    max_tokens: int = 2000

    # Redis
    redis_url: str = "redis://localhost:6379"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# ❌ BAD - Direct os.getenv
import os
OPENAI_KEY = os.getenv("OPENAI_API_KEY")  # No type safety, no validation
```

## Testing

### Use pytest

```python
# test_conversation_service.py
import pytest
from app.services.conversation_service import ConversationService
from app.models.schemas import ConversationRequest, Message

@pytest.fixture
def conversation_service():
    return ConversationService()

@pytest.mark.asyncio
async def test_process_conversation(conversation_service):
    # Arrange
    request = ConversationRequest(
        call_sid="CS123",
        customer_message=Message(
            speaker="customer",
            message="I need to book a service",
            timestamp="2024-01-01T12:00:00Z"
        )
    )

    # Act
    response = await conversation_service.process(request)

    # Assert
    assert response.ai_response.speaker == "AI"
    assert len(response.ai_response.message) > 0
    assert isinstance(response.should_hangup, bool)
```

## Performance

### Use Connection Pooling

```python
# ✅ GOOD - Connection pooling
import httpx

class OpenAIClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20)
        )

    async def generate(self, prompt: str) -> str:
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            json={"prompt": prompt}
        )
        return response.json()

    async def close(self):
        await self.client.aclose()

# ❌ BAD - New connection each time
async def generate(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(...)
```

### Cache Expensive Operations

```python
# ✅ GOOD - Caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_system_prompt(service_type: str) -> str:
    """Get system prompt (cached)."""
    return f"You are a helpful assistant for {service_type} services..."
```

## Security

### Validate All Inputs

```python
# ✅ GOOD - Input validation
from pydantic import BaseModel, Field, validator

class ConversationRequest(BaseModel):
    call_sid: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=10000)

    @validator('call_sid')
    def validate_call_sid(cls, v):
        if not v.startswith('CA'):
            raise ValueError('Invalid Call SID format')
        return v
```

### Don't Expose Internal Errors

```python
# ✅ GOOD - Generic error message
try:
    result = await process_sensitive_data()
except Exception as e:
    logger.error(f"Internal error: {e}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="Internal server error"  # Don't expose details
    )

# ❌ BAD - Exposing internal details
try:
    result = await process_sensitive_data()
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Database connection failed: {e}"  # TOO MUCH INFO
    )
```

## Code Review Checklist (AI Service)

- [ ] All functions have type hints
- [ ] All constants are UPPER_SNAKE_CASE
- [ ] Using snake_case for functions/variables
- [ ] Using PascalCase for classes
- [ ] Pydantic models for request/response
- [ ] Async/await for I/O operations
- [ ] Proper error handling with HTTPException
- [ ] Using logging module (not print)
- [ ] Docstrings for public functions
- [ ] Environment variables via Pydantic Settings
- [ ] Input validation
- [ ] No hardcoded secrets
- [ ] Connection pooling for external APIs
- [ ] Tests written with pytest
- [ ] Ruff linting passes
