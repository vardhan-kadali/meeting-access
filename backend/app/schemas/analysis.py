from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from app.schemas.deadline import DeadlineInterpretation

class FindingCategoryEnum(str, Enum):
    DISABILITY_ACCOMMODATION_CONTACT = "disability_accommodation_contact"
    ACCOMMODATION_REQUEST_METHODS = "accommodation_request_methods"
    EXPLICIT_ACCOMMODATION_DEADLINES = "explicit_accommodation_deadlines"
    ALTERNATIVE_DOCUMENT_FORMATS = "alternative_document_formats"
    ASL_SIGN_LANGUAGE_INTERPRETATION = "asl_sign_language_interpretation"
    LIVE_CAPTIONING = "live_captioning"
    ASSISTED_LISTENING_DEVICES = "assisted_listening_devices"
    REMOTE_PARTICIPATION_INSTRUCTIONS = "remote_participation_instructions"
    PUBLIC_COMMENT_INSTRUCTIONS = "public_comment_instructions"

class FindingStatusEnum(str, Enum):
    FOUND = "found"
    UNCLEAR = "unclear"
    NOT_FOUND_IN_DOCUMENT = "not_found_in_document"
    NOT_APPLICABLE = "not_applicable"

CATEGORY_METADATA = {
    FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT: {
        "label": "Disability Accommodation Contact Information",
        "description": "Specific contact person, office, email, phone number, or TTY/TDD for requesting accommodations."
    },
    FindingCategoryEnum.ACCOMMODATION_REQUEST_METHODS: {
        "label": "Accommodation Request Methods",
        "description": "Instructions and procedures on how a participant can submit an accommodation request."
    },
    FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES: {
        "label": "Explicit Accommodation Request Deadlines",
        "description": "Explicit advance notice timeframes required to request disability accommodations (e.g., 72 hours, 3 working days)."
    },
    FindingCategoryEnum.ALTERNATIVE_DOCUMENT_FORMATS: {
        "label": "Alternative Document / Agenda Formats",
        "description": "Instructions for obtaining the agenda or meeting materials in accessible formats (large print, braille, electronic)."
    },
    FindingCategoryEnum.ASL_SIGN_LANGUAGE_INTERPRETATION: {
        "label": "Sign Language / ASL Interpretation",
        "description": "Information on requesting American Sign Language (ASL) or certified interpreters, including separate notice timelines."
    },
    FindingCategoryEnum.LIVE_CAPTIONING: {
        "label": "Live Captions / Captioning",
        "description": "Information regarding closed captioning, automated captions, or live CART services for the meeting."
    },
    FindingCategoryEnum.ASSISTED_LISTENING_DEVICES: {
        "label": "Assisted Listening Devices",
        "description": "Availability and checkout instructions for assistive listening headsets, loops, or receivers in the meeting facility."
    },
    FindingCategoryEnum.REMOTE_PARTICIPATION_INSTRUCTIONS: {
        "label": "Remote Participation Instructions",
        "description": "Instructions for attending remotely via teleconference, video platform (Zoom, Teams), or telephone dial-in."
    },
    FindingCategoryEnum.PUBLIC_COMMENT_INSTRUCTIONS: {
        "label": "Public Comment Instructions",
        "description": "Procedures, time limits, and submission deadlines for providing public comments in person or remotely."
    },
}

class RawFindingItem(BaseModel):
    """Raw structured finding returned by the LLM before Python verification."""
    category: str
    status: FindingStatusEnum
    quote: Optional[str] = None
    page_number: Optional[int] = None
    explanation: str
    suggested_action: str

class FindingItem(BaseModel):
    """Final, verified finding."""
    category: FindingCategoryEnum
    category_label: str
    status: FindingStatusEnum
    quote: Optional[str] = None
    page_number: Optional[int] = None
    is_quote_verified: bool = False
    verification_notes: Optional[str] = None
    explanation: str
    suggested_action: str

class DocumentAnalysisResponse(BaseModel):
    filename: str
    total_pages: int
    extraction_status: str
    model_used: str
    analyzed_at: str
    findings: List[FindingItem]
    verified_evidence_count: int
    missing_evidence_count: int
    unclear_evidence_count: int
    ocr_warning: Optional[str] = None
    deadline_interpretation: Optional[DeadlineInterpretation] = Field(
        None,
        description="Transparent interpretation of verified accommodation request deadline"
    )
