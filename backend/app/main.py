import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fairlens")

# Ensure database tables exist
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.warning(f"Database initialization notice: {e}")

app = FastAPI(
    title="FairLens AI 2.0 API",
    description="Enterprise Responsible AI Governance Platform",
    version="2.0.0"
)

# Build origins list
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)
if settings.VERCEL_ORIGIN:
    origins.append(settings.VERCEL_ORIGIN)
if settings.ALLOWED_ORIGINS:
    for item in settings.ALLOWED_ORIGINS.split(","):
        clean_item = item.strip()
        if clean_item and clean_item not in origins:
            origins.append(clean_item)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import api_router
from app.routes import upload, analyze, explain, fix, history

app.include_router(api_router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(explain.router, prefix="/api", tags=["explain"])
app.include_router(fix.router, prefix="/api", tags=["fix"])
app.include_router(history.router, prefix="/api", tags=["history"])

@app.get("/")
def root():
    return {"message": "FairLens AI 2.0 API is running", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "FairLens AI API", "version": "2.0.0"}

@app.get("/ready")
def ready():
    from app.services import firebase_service
    return {
        "status": "ready",
        "firebase_configured": firebase_service.db is not None,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "frontend_url": settings.FRONTEND_URL,
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

