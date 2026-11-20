from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import sys
from app.config import settings
from app.routers.documents import router as documents_router
from app.routers.analysis import router as analysis_router

app = FastAPI(
    title="MEETING ACCESS API",
    description="Civic accessibility intelligence backend for California public meeting agendas.",
    version="0.1.0",
)

# Configure CORS
# When '*' is configured in origins, credentials cannot be enabled per CORS specification.
cors_origins = settings.CORS_ORIGINS
allow_all = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https://.*\.pages\.dev$",
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(documents_router)
app.include_router(analysis_router)

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint returning service status, model configuration,
    and Python environment verification. Polled by Render and Cloudflare during deployments.
    """
    return {
        "status": "healthy",
        "service": "MEETING ACCESS API",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "configured_gemini_model": settings.GEMINI_MODEL,
        "api_key_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"),
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
        "max_page_count": settings.MAX_PAGE_COUNT,
    }
