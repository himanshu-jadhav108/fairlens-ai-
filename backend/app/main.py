from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title="FairLens AI 2.0 API",
    description="Enterprise Responsible AI Governance Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
