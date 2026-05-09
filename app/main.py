from fastapi import FastAPI
from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "A prototype factory knowledge learning agent that captures, "
        "verifies, and retrieves operational knowledge from worker conversations."
    ),
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Factory Knowledge Agent API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env
    }