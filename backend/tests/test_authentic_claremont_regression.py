import pytest
import pdfplumber
from pathlib import Path
from app.schemas.analysis import (
    FindingCategoryEnum,
    FindingStatusEnum,
    RawFindingItem,
)
from app.services.verification_service import verify_findings
from app.services.pdf_extractor import extract_pdf_pages_in_memory

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "sample_data"
AUTHENTIC_PDF_PATH = SAMPLE_DATA_DIR / "11-10-26-city-council-agenda-only.pdf"

@pytest.fixture(scope="module")
def authentic_extracted_pages():
    assert AUTHENTIC_PDF_PATH.exists(), f"Authentic fixture missing at {AUTHENTIC_PDF_PATH}"
    with open(AUTHENTIC_PDF_PATH, "rb") as f:
        file_bytes = f.read()
    extraction = extract_pdf_pages_in_memory(file_bytes, AUTHENTIC_PDF_PATH.name)
    assert extraction.total_pages == 6
    return extraction.pages

def test_authentic_claremont_exact_quotes_pass_verification(authentic_extracted_pages):
    """Authentic Claremont quotes from Page 6 must pass verification."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="CONTACT THE CITY CLERK AT 909-399-5461 or 909-399-5463 “VOICE” OR 1-800-735-2929 “TT/TTY”",
            page_number=6,
            explanation="Authentic Claremont City Clerk contact numbers.",
            suggested_action="Contact City Clerk."
        ),
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE.",
            page_number=6,
            explanation="Authentic three-working-day qualified timeline.",
            suggested_action="Contact at least three working days prior if possible."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)

    contact_finding = next(f for f in verified if f.category == FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT)
    assert contact_finding.is_quote_verified is True
    assert "909-399-5461" in contact_finding.quote
    assert "1-800-735-2929" in contact_finding.quote

    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    assert deadline_finding.is_quote_verified is True
    assert "THREE (3) WORKING DAYS" in deadline_finding.quote
    assert "IF POSSIBLE" in deadline_finding.quote

def test_regression_catches_fabricated_phone_number(authentic_extracted_pages):
    """Must catch and reject synthetic phone number (909) 399-5460."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="contact the City Clerk at (909) 399-5460",
            page_number=6,
            explanation="Fabricated phone number.",
            suggested_action="Call number."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)
    contact_finding = next(f for f in verified if f.category == FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT)
    assert contact_finding.is_quote_verified is False
    assert "could not be located" in contact_finding.verification_notes

def test_regression_catches_fabricated_email_address(authentic_extracted_pages):
    """Must catch and reject synthetic email address cityclerk@ci.claremont.ca.us."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="cityclerk@ci.claremont.ca.us",
            page_number=6,
            explanation="Fabricated legacy email address.",
            suggested_action="Email clerk."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)
    contact_finding = next(f for f in verified if f.category == FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT)
    assert contact_finding.is_quote_verified is False
    assert "could not be located" in contact_finding.verification_notes

def test_regression_catches_72_hour_substitution(authentic_extracted_pages):
    """Must catch and reject replacement of three working days with 72 hours."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="Notification 72 hours prior to the meeting will enable the City to make reasonable arrangements",
            page_number=6,
            explanation="Fabricated 72 hour requirement.",
            suggested_action="Request 72h prior."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)
    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    assert deadline_finding.is_quote_verified is False
    assert "could not be located" in deadline_finding.verification_notes

def test_regression_catches_wrong_page_number(authentic_extracted_pages):
    """Must reject claiming the ADA notice is on Page 1 or Page 2 when it is on Page 6."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT.value,
            status=FindingStatusEnum.FOUND,
            quote="CONTACT THE CITY CLERK AT 909-399-5461 or 909-399-5463",
            page_number=2,  # Notice is on Page 6, not Page 2
            explanation="Wrong page citation.",
            suggested_action="Call clerk."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)
    contact_finding = next(f for f in verified if f.category == FindingCategoryEnum.DISABILITY_ACCOMMODATION_CONTACT)
    assert contact_finding.is_quote_verified is False
    assert "not on page 2" in contact_finding.verification_notes
    assert "page 6" in contact_finding.verification_notes

def test_regression_catches_public_comment_deadline_confusion(authentic_extracted_pages):
    """Must catch assigning Page 1 public comment 3 PM telephone cutoff to accommodation deadline."""
    raw = [
        RawFindingItem(
            category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES.value,
            status=FindingStatusEnum.FOUND,
            quote="Contact the City Clerk’s office by 3 PM the day of the meeting to provide your contact number",
            page_number=1,
            explanation="Confusing public comment telephone deadline with accommodation deadline.",
            suggested_action="Register by 3 PM."
        )
    ]
    verified = verify_findings(raw, authentic_extracted_pages, total_pages=6)
    deadline_finding = next(f for f in verified if f.category == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES)
    assert deadline_finding.is_quote_verified is False
    assert "Contextual verification rejected" in deadline_finding.verification_notes
