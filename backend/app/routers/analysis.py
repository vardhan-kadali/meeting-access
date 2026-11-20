from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.schemas.analysis import DocumentAnalysisResponse
from app.services.pdf_validator import validate_pdf_content_and_structure
from app.services.pdf_extractor import extract_pdf_pages_in_memory
from app.services.analysis_service import analyze_document_content

router = APIRouter(prefix="/api/documents", tags=["analysis"])

@router.post(
    "/analyze",
    response_model=DocumentAnalysisResponse,
    summary="Analyze PDF agenda for participation readiness",
    description="Extracts and analyzes participation, accommodation, and accessibility instructions with deterministic quote verification."
)
async def analyze_document(
    file: UploadFile = File(..., description="PDF meeting agenda to analyze")
):
    filename = file.filename or "unknown.pdf"

    # Enforce safe cleanup of UploadFile spooling resources
    try:
        try:
            file_bytes = await file.read()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read uploaded file stream."
            )

        # 1. Structural and limit validation
        validate_pdf_content_and_structure(
            file_bytes=file_bytes,
            filename=filename,
            max_size_mb=settings.MAX_UPLOAD_SIZE_MB,
            max_pages=settings.MAX_PAGE_COUNT,
        )

        # 2. Extract pages and calculate text density in memory
        extraction = extract_pdf_pages_in_memory(
            file_bytes=file_bytes,
            filename=filename
        )

        if extraction.overall_status == "no_extractable_text":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY if hasattr(status, "HTTP_422_UNPROCESSABLE_ENTITY") else 422,
                detail="No extractable text was found in this document (scanned image). AI analysis cannot proceed without OCR text."
            )

        # 3. Execute contextual AI extraction + Python deterministic verification
        analysis_result = analyze_document_content(
            filename=filename,
            extracted_pages=extraction.pages,
            total_pages=extraction.total_pages,
            ocr_warning=extraction.ocr_warning
        )

        return analysis_result

    finally:
        # Guarantee release of spooled temporary file descriptors
        await file.close()
