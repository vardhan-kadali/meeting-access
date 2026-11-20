from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from app.config import settings
from app.schemas.analysis import DocumentAnalysisResponse, SampleAgendaItem
from app.services.pdf_validator import validate_pdf_content_and_structure
from app.services.pdf_extractor import extract_pdf_pages_in_memory
from app.services.analysis_service import analyze_document_content

router = APIRouter(prefix="/api/documents", tags=["analysis"])

SAMPLE_DATA_DIR = Path(__file__).resolve().parents[3] / "sample_data"

SAMPLE_AGENDAS = {
    "claremont": SampleAgendaItem(
        id="claremont",
        title="City of Claremont City Council",
        jurisdiction="City of Claremont, California",
        date="November 10, 2026",
        pages=6,
        filename="11-10-26-city-council-agenda-only.pdf",
        highlight="Standard 3 working days qualified timeline ('if possible'), alternative formats, TTY relay, separate public comment cutoff."
    ),
    "berkeley": SampleAgendaItem(
        id="berkeley",
        title="City of Berkeley City Council",
        jurisdiction="City of Berkeley, California",
        date="March 10, 2026",
        pages=4,
        filename="2026-03-10-berkeley-council-agenda.pdf",
        highlight="Multi-category accommodations: Live B-TV captions, assistive listening devices in chambers, TDD line, 3 business days request window."
    ),
    "sanjose": SampleAgendaItem(
        id="sanjose",
        title="City of San José Planning Commission",
        jurisdiction="City of San José, California",
        date="May 10, 2023",
        pages=11,
        filename="sanjose-council-agenda-1101871.pdf",
        highlight="11-page Legistar agenda, past meeting detection, multiple ADA contacts, non-disability term suppression."
    ),
    "islavista": SampleAgendaItem(
        id="islavista",
        title="Isla Vista Community Services District",
        jurisdiction="Isla Vista CSD, California",
        date="October 27, 2026",
        pages=4,
        filename="10-27-2026-isla-vista-csd-agenda.pdf",
        highlight="Special district, bilingual English/Spanish notice, general advance notice without speculative deadline calculation."
    ),
}


@router.get(
    "/samples",
    response_model=List[SampleAgendaItem],
    summary="List available authentic California sample meeting agendas",
    description="Provides pre-loaded real California municipal and special-district agendas for quick judging validation."
)
async def list_sample_agendas() -> List[SampleAgendaItem]:
    return list(SAMPLE_AGENDAS.values())


@router.post(
    "/samples/{sample_id}/analyze",
    response_model=DocumentAnalysisResponse,
    summary="Analyze a pre-loaded authentic sample agenda",
    description="Runs the full extraction, AI analysis, quote verification, and deadline interpretation on a sample agenda."
)
async def analyze_sample_agenda(sample_id: str) -> DocumentAnalysisResponse:
    sample = SAMPLE_AGENDAS.get(sample_id.lower())
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample agenda '{sample_id}' not found. Available samples: {', '.join(SAMPLE_AGENDAS.keys())}"
        )

    file_path = SAMPLE_DATA_DIR / sample.filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sample agenda file '{sample.filename}' is missing from server storage."
        )

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # 1. Structural and limit validation
    validate_pdf_content_and_structure(
        file_bytes=file_bytes,
        filename=sample.filename,
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB,
        max_pages=settings.MAX_PAGE_COUNT,
    )

    # 2. Extract pages and calculate text density in memory
    extraction = extract_pdf_pages_in_memory(
        file_bytes=file_bytes,
        filename=sample.filename
    )

    # 3. Execute contextual AI extraction + Python deterministic verification
    analysis_result = analyze_document_content(
        filename=sample.filename,
        extracted_pages=extraction.pages,
        total_pages=extraction.total_pages,
        ocr_warning=extraction.ocr_warning
    )

    return analysis_result


@router.get(
    "/samples/{sample_id}/download",
    summary="Download original authentic sample PDF",
    description="Serves the exact binary bytes of the official government PDF."
)
async def download_sample_agenda(sample_id: str):
    sample = SAMPLE_AGENDAS.get(sample_id.lower())
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample agenda '{sample_id}' not found."
        )

    file_path = SAMPLE_DATA_DIR / sample.filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sample agenda file '{sample.filename}' is missing from server storage."
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=sample.filename
    )


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
