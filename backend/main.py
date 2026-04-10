import sys
from pathlib import Path
from app.ai import rag  # 新增这一行
from app.config import get_settings
from app.api import health, chat, call, summary, debug
from app.infrastructure.mongo import get_db
from app.api.chat import router as answer_router
from app.api.call import router as call_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add the app directory to Python path for absolute imports
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))


settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
)

load_dotenv()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(call.router, prefix=settings.api_prefix)
app.include_router(summary.router, prefix=settings.api_prefix)
app.include_router(rag.router, prefix=settings.api_prefix) 
app.include_router(answer_router)
app.include_router(call_router)  


app.include_router(debug.router, prefix=settings.api_prefix)



@app.get("/")
async def root():
    return {
        "message": "AI Service API",
        "version": settings.api_version,
        "environment": settings.environment,
    }

@app.get("/api/health/mongo")
async def test_mongo():
    db = get_db()
    return {"collections": db.list_collection_names()}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
