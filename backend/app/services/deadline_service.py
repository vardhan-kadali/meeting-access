import re
import datetime
from typing import List, Optional, Tuple
from dateutil import parser as date_parser

from app.schemas.analysis import FindingItem, FindingCategoryEnum, FindingStatusEnum
from app.schemas.document import PageExtractionResult
from app.schemas.deadline import (
    DeadlineInterpretation,
    InstructionStrengthEnum,
    CalculationStatusEnum,
)

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "72": 72,
    "48": 48,
    "24": 24,
}

QUALIFIER_PATTERNS = [
    (r"\bif possible\b", "if possible"),
    (r"\bwhen feasible\b", "when feasible"),
    (r"\bwhere feasible\b", "where feasible"),
    (r"\bshould\b", "should"),
    (r"\bplease allow\b", "please allow"),
    (r"\brecommended\b", "recommended"),
    (r"\bpreferred\b", "preferred"),
    (r"\bas early as possible\b", "as early as possible"),
    (r"\brequested\b", "requested"),
]

MANDATORY_PATTERNS = [
    r"\bmust\b",
    r"\bshall\b",
    r"\bno later than\b",
    r"\brequired\b",
    r"\bmandatory\b",
]

def extract_meeting_datetime(
    extracted_pages: List[PageExtractionResult]
) -> Tuple[Optional[datetime.date], Optional[str], Optional[str]]:
    """
    Extracts meeting date, meeting time, and title from the first page of the agenda.
    Returns (meeting_date, meeting_time_str, meeting_title).
    """
    if not extracted_pages:
        return None, None, None

    # Focus primarily on Page 1 where meeting headers are legally situated
    p1_text = extracted_pages[0].text

    # Extract date: e.g. "Tuesday November 10, 2026" or "November 10, 2026"
    date_match = re.search(
        r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})",
        p1_text,
        re.IGNORECASE
    )
    meeting_date: Optional[datetime.date] = None
    meeting_date_str: Optional[str] = None
    if date_match:
        try:
            month_str, day_str, year_str = date_match.group(1), date_match.group(2), date_match.group(3)
            parsed_dt = date_parser.parse(f"{month_str} {day_str} {year_str}")
            meeting_date = parsed_dt.date()
            meeting_date_str = meeting_date.strftime("%B %d, %Y")
        except Exception:
            meeting_date = None

    # Extract time: e.g. "6:30 PM", "7:00 P.M.", "10:00 AM"
    time_match = re.search(
        r"(\b\d{1,2}:\d{2}\s*(?:AM|PM|A\.M\.|P\.M\.))",
        p1_text,
        re.IGNORECASE
    )
    meeting_time_str = time_match.group(1).strip() if time_match else None

    # Title match from top lines
    lines = [line.strip() for line in p1_text.split("\n") if line.strip()]
    meeting_title = lines[0] if lines else "Public Meeting"

    return meeting_date, meeting_time_str, meeting_title


def classify_instruction_strength(quote: str) -> Tuple[InstructionStrengthEnum, Optional[str]]:
    """
    Classifies the strength of an accommodation instruction.
    Critical: Qualifiers such as 'if possible' always take precedence over mandatory terms.
    """
    if not quote or quote.strip() == "":
        return InstructionStrengthEnum.UNCLEAR, None

    quote_lower = quote.lower()

    # 1. Check for explicit qualifiers
    for pattern, label in QUALIFIER_PATTERNS:
        if re.search(pattern, quote_lower):
            return InstructionStrengthEnum.RECOMMENDED_OR_QUALIFIED, label

    # 2. Check for explicit mandatory terms
    for pattern in MANDATORY_PATTERNS:
        if re.search(pattern, quote_lower):
            return InstructionStrengthEnum.MANDATORY, None

    # 3. Check if numerical timeframe exists without mandatory words
    if any(k in quote_lower for k in ["hours", "working days", "business days", "days prior", "advance notice"]):
        return InstructionStrengthEnum.INFORMATIONAL, None

    return InstructionStrengthEnum.UNCLEAR, None


def interpret_accommodation_deadline(
    deadline_finding: Optional[FindingItem],
    extracted_pages: List[PageExtractionResult],
    reference_date: Optional[datetime.date] = None
) -> Optional[DeadlineInterpretation]:
    """
    Interprets verified accommodation request deadlines deterministically.
    """
    # 1. Guard: Only process verified explicit_accommodation_deadlines
    if not deadline_finding:
        return None

    if deadline_finding.category != FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES:
        return None

    meeting_date, meeting_time_str, meeting_title = extract_meeting_datetime(extracted_pages)
    meeting_date_str = meeting_date.strftime("%B %d, %Y") if meeting_date else None

    if reference_date is None:
        # Default to current date (2026-11-20 in system metadata)
        reference_date = datetime.date(2026, 11, 20)

    is_past_meeting = bool(meeting_date and meeting_date < reference_date)

    # 2. Guard: Unverified or unlocated evidence cannot produce a calculated date
    if (
        deadline_finding.status != FindingStatusEnum.FOUND
        or not deadline_finding.is_quote_verified
        or not deadline_finding.quote
        or deadline_finding.page_number is None
    ):
        return DeadlineInterpretation(
            original_instruction=deadline_finding.quote or "No explicit deadline found in document.",
            page_number=deadline_finding.page_number or 0,
            is_verified=False,
            instruction_strength=InstructionStrengthEnum.UNCLEAR,
            qualifier_text=None,
            target_event=meeting_title or "Meeting",
            meeting_date_str=meeting_date_str,
            meeting_time_str=meeting_time_str,
            is_past_meeting=is_past_meeting,
            days_offset=None,
            offset_unit=None,
            calculated_date=None,
            calculated_time=None,
            calculation_status=CalculationStatusEnum.CANNOT_CALCULATE,
            assumptions=[],
            limitations=[
                "Unverified evidence: An accommodation request deadline was either not found or could not be verified in the document.",
                "No deadline calculation can be performed without verified source evidence."
            ],
            explanation="No verified accommodation deadline was available to interpret."
        )

    quote = deadline_finding.quote
    page_num = deadline_finding.page_number

    # 3. Classify instruction strength
    strength, qualifier = classify_instruction_strength(quote)
    quote_lower = quote.lower()

    # 4. Parse numerical rule
    days_offset: Optional[int] = None
    offset_unit: Optional[str] = None

    # Check Working Days / Business Days: e.g. "three (3) working days", "3 business days"
    working_days_match = re.search(
        r"(?:at least\s+)?(\d+|one|two|three|four|five|six|seven|ten)(?:\s*\(\d+\))?\s*(?:working|business)\s*days",
        quote_lower
    )
    # Check Hours: e.g. "72 hours", "48 hours"
    hours_match = re.search(
        r"(?:at least\s+)?(\d+)\s*(?:hours|hrs)",
        quote_lower
    )
    # Check Explicit Calendar Days: e.g. "3 calendar days"
    calendar_days_match = re.search(
        r"(?:at least\s+)?(\d+|one|two|three|four|five|six|seven|ten)(?:\s*\(\d+\))?\s*calendar\s*days",
        quote_lower
    )
    # Check Ambiguous Days: e.g. "three days", "3 days prior"
    ambiguous_days_match = re.search(
        r"(?:at least\s+)?(\d+|one|two|three|four|five|six|seven|ten)(?:\s*\(\d+\))?\s*days",
        quote_lower
    )

    if working_days_match:
        val_str = working_days_match.group(1).lower()
        days_offset = NUMBER_WORDS.get(val_str, int(val_str) if val_str.isdigit() else None)
        offset_unit = "working_days"
    elif calendar_days_match:
        val_str = calendar_days_match.group(1).lower()
        days_offset = NUMBER_WORDS.get(val_str, int(val_str) if val_str.isdigit() else None)
        offset_unit = "calendar_days"
    elif hours_match:
        val_str = hours_match.group(1)
        days_offset = int(val_str) if val_str.isdigit() else None
        offset_unit = "hours"
    elif ambiguous_days_match:
        val_str = ambiguous_days_match.group(1).lower()
        days_offset = NUMBER_WORDS.get(val_str, int(val_str) if val_str.isdigit() else None)
        offset_unit = "ambiguous_days"

    # 5. Deterministic Date Calculation
    calculated_date: Optional[str] = None
    calculated_time: Optional[str] = None
    calculation_status = CalculationStatusEnum.CANNOT_CALCULATE
    assumptions: List[str] = []
    limitations: List[str] = []

    # Check meeting date availability
    if not meeting_date:
        limitations.append("Meeting date was not identified on the agenda; date calculation cannot proceed.")
    elif days_offset is None or offset_unit is None:
        limitations.append("The accommodation notice does not state an explicit numerical timeframe.")
    elif offset_unit == "ambiguous_days":
        # Rule: Do not automatically interpret ambiguous "three days" as calendar days or working days
        limitations.append(
            f"The agenda states '{days_offset} days' without specifying whether calendar days or working/business days are intended. "
            "Calculation is withheld to prevent misleading assumptions."
        )
    elif offset_unit == "working_days":
        # Subtract working days (Monday - Friday)
        curr = meeting_date
        subtracted = 0
        while subtracted < days_offset:
            curr -= datetime.timedelta(days=1)
            if curr.weekday() < 5:  # Monday through Friday
                subtracted += 1

        calculated_date = curr.strftime("%B %d, %Y")
        calculation_status = CalculationStatusEnum.PROVISIONAL

        assumptions.append(
            f"Calculated by subtracting {days_offset} weekdays (excluding Saturday and Sunday) from {meeting_date.strftime('%A, %B %d, %Y')}."
        )
        assumptions.append("Assumes standard Monday-through-Friday municipal office schedules.")

        limitations.append(
            "Provisional: Applicable California state, county, or municipal holidays were not authoritatively checked "
            "and could shift the deadline earlier if city offices are closed."
        )
        limitations.append(
            "Federal holiday calendars do not cover all California state, judicial, or local municipal closures."
        )
        limitations.append("This calculation is attendee support guidance, not a binding legal determination.")

    elif offset_unit == "hours":
        # Hour-based calculation requires meeting time
        if not meeting_time_str:
            limitations.append(
                f"Hour-based rule ({days_offset} hours) requires the exact meeting start time, which was not established in the agenda. "
                "No arbitrary time-of-day cutoff was invented."
            )
        else:
            try:
                dt_str = f"{meeting_date.strftime('%Y-%m-%d')} {meeting_time_str.replace('.', '')}"
                meeting_dt = date_parser.parse(dt_str)
                deadline_dt = meeting_dt - datetime.timedelta(hours=days_offset)
                calculated_date = deadline_dt.strftime("%B %d, %Y")
                calculated_time = deadline_dt.strftime("%I:%M %p").lstrip("0")
                calculation_status = CalculationStatusEnum.CALCULATED

                assumptions.append(
                    f"Subtracted {days_offset} hours from meeting start time ({meeting_time_str}) on {meeting_date.strftime('%B %d, %Y')} (California Pacific Time)."
                )
                limitations.append("Assumes California Pacific Time (PT).")
                limitations.append("This is an attendee support estimate, not a binding legal determination.")
            except Exception:
                limitations.append(f"Failed to parse meeting time '{meeting_time_str}' accurately.")

    elif offset_unit == "calendar_days":
        calc_dt = meeting_date - datetime.timedelta(days=days_offset)
        calculated_date = calc_dt.strftime("%B %d, %Y")
        calculation_status = CalculationStatusEnum.CALCULATED
        assumptions.append(f"Subtracted {days_offset} calendar days from {meeting_date.strftime('%B %d, %Y')}.")
        limitations.append("This is an attendee support estimate, not a binding legal determination.")

    # 6. Qualification & Past Meeting Disclosures
    if qualifier:
        limitations.append(
            f"Qualified instruction: The agenda requests advance notice '{qualifier}' rather than imposing a strict mandatory cutoff."
        )

    if is_past_meeting and meeting_date:
        limitations.append(
            f"Past meeting: This meeting was scheduled for {meeting_date.strftime('%B %d, %Y')} and has already occurred."
        )

    # 7. Formulate Plain Language Explanation
    if calculation_status == CalculationStatusEnum.PROVISIONAL:
        explanation = (
            f"The agenda requests accommodation notice at least {days_offset} working days prior to the meeting"
            + (f" ({qualifier})" if qualifier else "")
            + f". Counting back {days_offset} weekdays from {meeting_date.strftime('%A, %B %d, %Y')} results in {calculated_date}."
        )
    elif calculation_status == CalculationStatusEnum.CALCULATED:
        explanation = (
            f"The agenda specifies an accommodation advance notice of {days_offset} {offset_unit.replace('_', ' ')}."
            f" Based on the meeting schedule, the estimated request deadline is {calculated_date}"
            + (f" at {calculated_time}" if calculated_time else "")
            + "."
        )
    else:
        explanation = (
            "An accommodation instruction was identified, but an exact date could not be calculated safely. "
            + (limitations[0] if limitations else "Review meeting agenda details.")
        )

    return DeadlineInterpretation(
        original_instruction=quote,
        page_number=page_num,
        is_verified=True,
        instruction_strength=strength,
        qualifier_text=qualifier,
        target_event=meeting_title or "City Council Meeting",
        meeting_date_str=meeting_date_str,
        meeting_time_str=meeting_time_str,
        is_past_meeting=is_past_meeting,
        days_offset=days_offset,
        offset_unit=offset_unit,
        calculated_date=calculated_date,
        calculated_time=calculated_time,
        calculation_status=calculation_status,
        assumptions=assumptions,
        limitations=limitations,
        explanation=explanation
    )
