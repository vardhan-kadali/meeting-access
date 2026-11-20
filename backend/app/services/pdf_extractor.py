import io
from datetime import datetime, timezone
from typing import List, Tuple
import pdfplumber

from app.schemas.document import (
    PageExtractionResult,
    PageExtractionStatusEnum,
    ExtractionStatusEnum,
    DocumentExtractionResponse,
)

# Threshold for classifying page text density
MIN_TEXT_CHARS_THRESHOLD = 30

def extract_pdf_pages_in_memory(
    file_bytes: bytes,
    filename: str
) -> DocumentExtractionResponse:
    """
    Extracts text from all pages of a PDF document using pdfplumber in memory.
    Preserves 1-based physical page numbers and unaltered text.
    """
    page_results: List[PageExtractionResult] = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        total_pages = len(pdf.pages)

        for index, page in enumerate(pdf.pages):
            physical_page_num = index + 1
            raw_text = page.extract_text() or ""
            # Character count based on stripped text
            char_count = len(raw_text.strip())

            if char_count == 0:
                page_status = PageExtractionStatusEnum.EMPTY_OR_IMAGE
            elif char_count < MIN_TEXT_CHARS_THRESHOLD:
                # Page contains negligible text, e.g., only a solitary page number or stamp
                page_status = PageExtractionStatusEnum.LOW_TEXT
            else:
                page_status = PageExtractionStatusEnum.TEXT_EXTRACTED

            page_results.append(
                PageExtractionResult(
                    page_number=physical_page_num,
                    text=raw_text,
                    char_count=char_count,
                    status=page_status,
                )
            )

    overall_status, ocr_warning = _determine_overall_status(page_results, total_pages)

    return DocumentExtractionResponse(
        filename=filename,
        file_size_bytes=len(file_bytes),
        total_pages=total_pages,
        overall_status=overall_status,
        ocr_warning=ocr_warning,
        pages=page_results,
        extracted_at=datetime.now(timezone.utc).isoformat(),
    )

def _determine_overall_status(
    pages: List[PageExtractionResult],
    total_pages: int
) -> Tuple[ExtractionStatusEnum, str | None]:
    """
    Calculates overall technical extraction status and generates non-judgmental OCR advisory.
    """
    if total_pages == 0:
        return ExtractionStatusEnum.NO_EXTRACTABLE_TEXT, "Document contains no pages."

    empty_count = sum(1 for p in pages if p.status == PageExtractionStatusEnum.EMPTY_OR_IMAGE)
    low_count = sum(1 for p in pages if p.status == PageExtractionStatusEnum.LOW_TEXT)
    full_count = sum(1 for p in pages if p.status == PageExtractionStatusEnum.TEXT_EXTRACTED)

    # 1. All pages have usable text
    if full_count == total_pages:
        return ExtractionStatusEnum.TEXT_EXTRACTED, None

    # 2. Entire document has zero extractable text
    if empty_count == total_pages:
        return (
            ExtractionStatusEnum.NO_EXTRACTABLE_TEXT,
            "No extractable text was found in this document. It appears to be an image-only or scanned PDF. "
            "An OCR tool or an accessible digital text version from the public agency is recommended to inspect participation instructions."
        )

    # 3. Majority of pages are empty or have negligible text
    unusable_ratio = (empty_count + low_count) / total_pages
    if unusable_ratio >= 0.5:
        return (
            ExtractionStatusEnum.LIKELY_SCANNED,
            "The majority of pages in this document contain minimal or no selectable text, suggesting it is a scanned document. "
            "Portions of meeting information or accessibility notices may require OCR or direct confirmation with the public agency."
        )

    # 4. Mix of text pages and some empty/low pages
    return (
        ExtractionStatusEnum.PARTIALLY_EXTRACTED,
        "Some pages in this document contain little or no extractable text. "
        "If accessibility notices are located on those pages, an OCR scan or agency inquiry may be needed."
    )
