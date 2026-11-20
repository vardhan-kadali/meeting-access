import pytest
from pathlib import Path
from app.services.pdf_extractor import extract_pdf_pages_in_memory
from app.services.verification_service import verify_findings
from app.services.deadline_service import interpret_accommodation_deadline
from app.schemas.analysis import (
    FindingCategoryEnum,
    FindingStatusEnum,
    RawFindingItem,
)
from app.schemas.deadline import InstructionStrengthEnum, CalculationStatusEnum

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "sample_data"

BERKELEY_PDF = SAMPLE_DATA_DIR / "2026-03-10-berkeley-council-agenda.pdf"
SANJOSE_PDF = SAMPLE_DATA_DIR / "sanjose-council-agenda-1101871.pdf"
ISLA_VISTA_PDF = SAMPLE_DATA_DIR / "10-27-2026-isla-vista-csd-agenda.pdf"
CLAREMONT_PDF = SAMPLE_DATA_DIR / "11-10-26-city-council-agenda-only.pdf"


def test_authentic_fixtures_exist():
    """Verify all authentic California government agenda fixtures exist in sample_data/."""
    assert BERKELEY_PDF.exists(), f"Missing {BERKELEY_PDF}"
    assert SANJOSE_PDF.exists(), f"Missing {SANJOSE_PDF}"
    assert ISLA_VISTA_PDF.exists(), f"Missing {ISLA_VISTA_PDF}"
    assert CLAREMONT_PDF.exists(), f"Missing {CLAREMONT_PDF}"


def test_berkeley_agenda_extraction_and_verification():
    """Test City of Berkeley: multi-category accommodations (captions, listening devices, TDD, deadline)."""
    with open(BERKELEY_PDF, "rb") as f:
        bytes_data = f.read()

    ext = extract_pdf_pages_in_memory(bytes_data, BERKELEY_PDF.name)
    assert ext.total_pages == 4

    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="(510) 981-6347 (TDD) at least three business days before the meeting date.",
            page_number=3,
            explanation="Berkeley requires requests at least three business days prior.",
            suggested_action="Contact Disability Services specialist at least 3 business days in advance."
        ),
        RawFindingItem(
            category=FindingCategoryEnum.LIVE_CAPTIONING.value,
            status=FindingStatusEnum.FOUND,
            quote="Live captioned broadcasts of Council meetings are available on B-TV (Channel 33) and via internet video stream.",
            page_number=1,
            explanation="Live captions provided on television broadcast and stream.",
            suggested_action="Access live captioned stream or B-TV broadcast."
        ),
        RawFindingItem(
            category=FindingCategoryEnum.ASSISTED_LISTENING_DEVICES.value,
            status=FindingStatusEnum.FOUND,
            quote="In addition, assisted listening devices for the hearing impaired are available from the City Clerk prior to the meeting, and are to be returned before the end of the meeting.",
            page_number=3,
            explanation="Assisted listening devices available from City Clerk in chambers.",
            suggested_action="Request listening device from City Clerk before meeting starts."
        ),
    ]

    verified = verify_findings(raw, ext.pages, ext.total_pages)
    for finding in verified:
        if finding.status == FindingStatusEnum.FOUND:
            assert finding.is_quote_verified is True
            assert finding.page_number in (1, 3)

    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    dl = interpret_accommodation_deadline(deadline_finding, ext.pages)
    assert dl is not None
    assert dl.calculated_date == "March 05, 2026"
    assert dl.calculation_status == CalculationStatusEnum.PROVISIONAL


def test_sanjose_agenda_extraction_and_verification():
    """Test City of San José: Legistar agenda, past meeting detection, non-disability false positive avoidance."""
    with open(SANJOSE_PDF, "rb") as f:
        bytes_data = f.read()

    ext = extract_pdf_pages_in_memory(bytes_data, SANJOSE_PDF.name)
    assert ext.total_pages == 11

    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="as soon as possible, but at least three business days before any meeting or event.",
            page_number=3,
            explanation="San Jose alternative format request deadline.",
            suggested_action="Submit request at least 3 business days before meeting."
        ),
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="Accommodations: Any member of the public who needs accommodations should email the ADA Coordinator at ADA@sanjoseca.gov or by calling (408) 535-8430.",
            page_number=3,
            explanation="San Jose ADA Coordinator contact information.",
            suggested_action="Email ADA@sanjoseca.gov or call (408) 535-8430."
        ),
    ]

    verified = verify_findings(raw, ext.pages, ext.total_pages)
    for finding in verified:
        if finding.status == FindingStatusEnum.FOUND:
            assert finding.is_quote_verified is True
            assert finding.page_number == 3

    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    dl = interpret_accommodation_deadline(deadline_finding, ext.pages)
    assert dl is not None
    assert dl.is_past_meeting is True
    assert dl.calculated_date == "May 05, 2023"
    assert dl.target_event is not None


def test_isla_vista_csd_agenda_extraction_and_verification():
    """Test Isla Vista CSD: Special district, bilingual accommodation notice, safely withholds speculative date calculation."""
    with open(ISLA_VISTA_PDF, "rb") as f:
        bytes_data = f.read()

    ext = extract_pdf_pages_in_memory(bytes_data, ISLA_VISTA_PDF.name)
    assert ext.total_pages == 4

    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="Please address all requests and questions regarding the meeting to General Manager Jonathan Abboud [(310) 734-9791 / generalmanager@islavistacsd.com] prior to the meeting date.",
            page_number=4,
            explanation="Isla Vista CSD General Manager contact information.",
            suggested_action="Contact Jonathan Abboud at (310) 734-9791 or generalmanager@islavistacsd.com."
        ),
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="Please address all requests and questions regarding the meeting to General Manager Jonathan Abboud [(310) 734-9791 / generalmanager@islavistacsd.com] prior to the meeting date.",
            page_number=4,
            explanation="Accommodation request timing instruction ('prior to the meeting date' without specific days).",
            suggested_action="Submit request prior to meeting date."
        ),
    ]

    verified = verify_findings(raw, ext.pages, ext.total_pages)
    for finding in verified:
        if finding.status == FindingStatusEnum.FOUND:
            assert finding.is_quote_verified is True
            assert finding.page_number == 4

    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    dl = interpret_accommodation_deadline(deadline_finding, ext.pages)
    assert dl is not None
    # No arbitrary numerical rule or hallucinated deadline calculation
    assert dl.calculated_date is None
    assert dl.calculation_status == CalculationStatusEnum.CANNOT_CALCULATE
