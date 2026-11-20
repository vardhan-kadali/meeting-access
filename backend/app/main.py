from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import sys
from app.config import settings

app = FastAPI(
    title="MEETING ACCESS API",
    description="Civic accessibility intelligence backend for California public meeting agendas.",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint returning service status, model configuration,
    and Python environment verification.
    """
    return {
        "status": "healthy",
        "service": "MEETING ACCESS API",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "configured_gemini_model": settings.GEMINI_MODEL,
        "api_key_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"),
    }
