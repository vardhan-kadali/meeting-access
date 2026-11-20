import io
from fastapi import HTTPException, status
from pypdf import PdfReader
from pypdf.errors import PdfReadError

def validate_pdf_content_and_structure(
    file_bytes: bytes,
    filename: str,
    max_size_mb: int = 15,
    max_pages: int = 100
) -> int:
    """
    Validates PDF file integrity, signature, encryption, and limits in memory.
    Returns total page count if valid, or raises HTTPException with clear error details.
    """
    # 1. Reject empty files
    if not file_bytes or len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes)."
        )

    # 2. Check filename extension
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .pdf files are accepted."
        )

    # 3. Check upload size limit
    max_bytes = max_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            detail=f"File exceeds maximum allowed size of {max_size_mb}MB ({len(file_bytes)} bytes uploaded)."
        )

    # 4. Check PDF magic bytes (%PDF-) within the first 1024 bytes
    header_sample = file_bytes[:1024]
    if b"%PDF-" not in header_sample:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF document: missing standard '%PDF-' file signature."
        )

    # 5. Inspect structure, encryption, and page count with pypdf
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except (PdfReadError, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed or unreadable PDF document."
        )

    # 6. Check for encryption
    if reader.is_encrypted:
        try:
            # Try blank password
            if not reader.decrypt(""):
                raise HTTPException(
                    status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
                    detail="This document is password-protected or encrypted and cannot be processed."
                )
        except Exception:
            raise HTTPException(
                status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
                detail="This document is password-protected or encrypted and cannot be processed."
            )

    # 7. Check page count
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF document contains 0 pages."
        )

    if total_pages > max_pages:
        raise HTTPException(
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            detail=f"Document exceeds maximum page limit of {max_pages} pages (contains {total_pages} pages)."
        )

    return total_pages
