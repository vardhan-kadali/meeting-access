from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.schemas.document import DocumentExtractionResponse
from app.services.pdf_validator import validate_pdf_content_and_structure
from app.services.pdf_extractor import extract_pdf_pages_in_memory

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post(
    "/extract",
    response_model=DocumentExtractionResponse,
    summary="Extract text and metadata from PDF meeting agenda",
    description="Validates and extracts page-by-page text from an uploaded PDF meeting agenda. Ephemeral processing with temporary spooled resources released immediately."
)
async def extract_document(
    file: UploadFile = File(..., description="PDF meeting agenda to extract")
):
    filename = file.filename or "unknown.pdf"

    try:
        # Read uploaded bytes into buffer
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

        # 2. Ephemeral page-by-page extraction
        try:
            result = extract_pdf_pages_in_memory(
                file_bytes=file_bytes,
                filename=filename
            )
            return result
        except Exception as exc:
            # Do not expose internal paths or stack traces
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while parsing the PDF document."
            )
    finally:
        # Guarantee closure and cleanup of any underlying spooled temporary files
        await file.close()
