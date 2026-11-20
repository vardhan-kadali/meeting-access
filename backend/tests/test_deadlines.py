import datetime
import pytest

from app.schemas.analysis import FindingItem, FindingCategoryEnum, FindingStatusEnum
from app.schemas.document import PageExtractionResult, PageExtractionStatusEnum
from app.schemas.deadline import InstructionStrengthEnum, CalculationStatusEnum
from app.services.deadline_service import (
    classify_instruction_strength,
    interpret_accommodation_deadline,
    extract_meeting_datetime,
)

def create_mock_page(page_num: int, text: str) -> PageExtractionResult:
    return PageExtractionResult(
        page_number=page_num,
        text=text,
        char_count=len(text),
        status=PageExtractionStatusEnum.TEXT_EXTRACTED
    )

# 1. "If possible" is preserved and never classified as mandatory
def test_if_possible_preserved_and_never_classified_as_mandatory():
    quote = "AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE."
    strength, qualifier = classify_instruction_strength(quote)
    assert strength == InstructionStrengthEnum.RECOMMENDED_OR_QUALIFIED
    assert qualifier == "if possible"
    assert strength != InstructionStrengthEnum.MANDATORY

    # Test with mandatory-looking prefix
    quote_must = "You must notify the City Clerk at least three days in advance, if possible."
    strength_must, qualifier_must = classify_instruction_strength(quote_must)
    assert strength_must == InstructionStrengthEnum.RECOMMENDED_OR_QUALIFIED
    assert qualifier_must == "if possible"

# 2. Three working days calculated correctly across a weekend
def test_three_working_days_calculated_across_weekend():
    # Meeting on Tuesday, November 10, 2026 at 6:30 PM
    pages = [
        create_mock_page(1, "Claremont City Council Meeting Agenda Tuesday November 10, 2026 6:30 PM"),
        create_mock_page(6, "CONTACT THE CITY CLERK AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE.")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE.",
        page_number=6,
        is_quote_verified=True,
        explanation="Three working days advance notice.",
        suggested_action="Contact clerk."
    )
    # Reference date set to Nov 1, 2026 (future meeting scenario)
    interp = interpret_accommodation_deadline(finding, pages, reference_date=datetime.date(2026, 11, 1))
    assert interp is not None
    assert interp.calculated_date == "November 05, 2026"
    assert interp.days_offset == 3
    assert interp.offset_unit == "working_days"
    assert interp.instruction_strength == InstructionStrengthEnum.RECOMMENDED_OR_QUALIFIED
    assert interp.qualifier_text == "if possible"

# 3. Holiday uncertainty is disclosed
def test_holiday_uncertainty_is_disclosed():
    pages = [
        create_mock_page(1, "City Council Meeting Agenda Tuesday November 10, 2026 6:30 PM")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Please contact staff three working days prior to the meeting.",
        page_number=1,
        is_quote_verified=True,
        explanation="Notice.",
        suggested_action="Contact."
    )
    interp = interpret_accommodation_deadline(finding, pages, reference_date=datetime.date(2026, 11, 1))
    assert interp is not None
    assert interp.calculation_status == CalculationStatusEnum.PROVISIONAL
    # Ensure limitations explicitly mention holiday uncertainty and California context
    limitation_text = " ".join(interp.limitations).lower()
    assert "holiday" in limitation_text
    assert "california" in limitation_text
    assert "provisional" in limitation_text

# 4. Past meetings receive the correct status
def test_past_meeting_status():
    # Meeting on Nov 10, 2026 evaluated against reference date Nov 20, 2026
    pages = [
        create_mock_page(1, "Claremont City Council Tuesday November 10, 2026 6:30 PM")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE.",
        page_number=1,
        is_quote_verified=True,
        explanation="Notice.",
        suggested_action="Contact."
    )
    interp = interpret_accommodation_deadline(finding, pages, reference_date=datetime.date(2026, 11, 20))
    assert interp is not None
    assert interp.is_past_meeting is True
    assert any("already occurred" in lim.lower() or "passed" in lim.lower() for lim in interp.limitations)

# 5. Missing meeting dates produce no calculated date
def test_missing_meeting_date_produces_no_calculated_date():
    pages = [
        create_mock_page(1, "Claremont City Council Meeting Agenda (No Date Provided)")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Notification 72 hours prior to the meeting is requested.",
        page_number=1,
        is_quote_verified=True,
        explanation="Notice.",
        suggested_action="Contact."
    )
    interp = interpret_accommodation_deadline(finding, pages)
    assert interp is not None
    assert interp.calculated_date is None
    assert interp.calculation_status == CalculationStatusEnum.CANNOT_CALCULATE
    assert any("meeting date was not identified" in lim.lower() for lim in interp.limitations)

# 6. Public-comment deadlines cannot trigger accommodation calculations
def test_public_comment_deadlines_cannot_trigger_accommodation_calculation():
    pages = [
        create_mock_page(1, "Claremont City Council Tuesday November 10, 2026 6:30 PM")
    ]
    # Finding is public comment instructions, not accommodation deadline
    comment_finding = FindingItem(
        category=FindingCategoryEnum.PUBLIC_COMMENT_INSTRUCTIONS,
        category_label="Public Comment Instructions",
        status=FindingStatusEnum.FOUND,
        quote="Written public comments must be submitted by 3:00 PM on the day of the meeting.",
        page_number=1,
        is_quote_verified=True,
        explanation="Public comment deadline.",
        suggested_action="Submit comments."
    )
    interp = interpret_accommodation_deadline(comment_finding, pages)
    # Must return None because it is not an accommodation deadline finding
    assert interp is None

# 7. Ambiguous "days" wording is not silently interpreted
def test_ambiguous_days_wording_not_silently_interpreted():
    pages = [
        create_mock_page(1, "City Council Meeting Agenda Tuesday November 10, 2026 6:30 PM")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Please notify staff at least three days prior to the meeting.",  # Ambiguous: not specified working or calendar
        page_number=1,
        is_quote_verified=True,
        explanation="Three days notice requested.",
        suggested_action="Contact staff."
    )
    interp = interpret_accommodation_deadline(finding, pages)
    assert interp is not None
    assert interp.offset_unit == "ambiguous_days"
    assert interp.calculated_date is None
    assert interp.calculation_status == CalculationStatusEnum.CANNOT_CALCULATE
    assert any("without specifying whether calendar days or working/business days" in lim for lim in interp.limitations)

# 8. Hour-based rules without meeting times are not calculated
def test_hour_based_rule_without_meeting_time_not_calculated():
    pages = [
        create_mock_page(1, "City Council Meeting Agenda November 10, 2026 (No start time given)")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Requests must be received at least 72 hours prior to the meeting.",
        page_number=1,
        is_quote_verified=True,
        explanation="72 hour rule.",
        suggested_action="Contact clerk."
    )
    interp = interpret_accommodation_deadline(finding, pages)
    assert interp is not None
    assert interp.calculated_date is None
    assert interp.calculation_status == CalculationStatusEnum.CANNOT_CALCULATE
    assert any("requires the exact meeting start time" in lim for lim in interp.limitations)

# 9. No arbitrary time-of-day cutoff is invented
def test_no_arbitrary_time_of_day_cutoff_invented():
    pages = [
        create_mock_page(1, "Claremont City Council Tuesday November 10, 2026 (No time specified)")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Notification 72 hours prior is requested.",
        page_number=1,
        is_quote_verified=True,
        explanation="72 hours.",
        suggested_action="Contact."
    )
    interp = interpret_accommodation_deadline(finding, pages)
    assert interp is not None
    # Must NOT invent "5:00 PM"
    assert interp.calculated_time is None
    assert interp.calculated_date is None
    assert any("no arbitrary time-of-day cutoff was invented" in lim.lower() for lim in interp.limitations)

# 10. Invalid or unverifiable evidence cannot produce a deadline
def test_unverifiable_evidence_cannot_produce_deadline():
    pages = [
        create_mock_page(1, "Claremont City Council Tuesday November 10, 2026 6:30 PM")
    ]
    finding = FindingItem(
        category=FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES,
        category_label="Explicit Accommodation Request Deadlines",
        status=FindingStatusEnum.FOUND,
        quote="Fabricated 72 hours quote that failed verification",
        page_number=1,
        is_quote_verified=False,  # Unverified!
        explanation="Unverified.",
        suggested_action="None."
    )
    interp = interpret_accommodation_deadline(finding, pages)
    assert interp is not None
    assert interp.is_verified is False
    assert interp.calculated_date is None
    assert interp.calculation_status == CalculationStatusEnum.CANNOT_CALCULATE
    assert any("unverified evidence" in lim.lower() for lim in interp.limitations)
