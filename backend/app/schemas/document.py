from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ExtractionStatusEnum(str, Enum):
    TEXT_EXTRACTED = "text_extracted"
    PARTIALLY_EXTRACTED = "partially_extracted"
    LIKELY_SCANNED = "likely_scanned"
    NO_EXTRACTABLE_TEXT = "no_extractable_text"

class PageExtractionStatusEnum(str, Enum):
    TEXT_EXTRACTED = "text_extracted"
    LOW_TEXT = "low_text"
    EMPTY_OR_IMAGE = "empty_or_image"

class PageExtractionResult(BaseModel):
    page_number: int = Field(..., description="Physical 1-based page number")
    text: str = Field(..., description="Extracted raw text from page, unaltered")
    char_count: int = Field(..., description="Total characters extracted from page")
    status: PageExtractionStatusEnum = Field(..., description="Page-level technical extraction status")

class DocumentExtractionResponse(BaseModel):
    filename: str = Field(..., description="Original name of the uploaded document")
    file_size_bytes: int = Field(..., description="File size in bytes")
    total_pages: int = Field(..., description="Total physical pages in document")
    overall_status: ExtractionStatusEnum = Field(..., description="Overall technical extraction status")
    ocr_warning: Optional[str] = Field(None, description="Informative warning if OCR or manual review is recommended")
    pages: List[PageExtractionResult] = Field(..., description="List of per-page extraction results")
    extracted_at: str = Field(..., description="ISO 8601 extraction timestamp")
