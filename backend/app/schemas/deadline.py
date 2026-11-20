from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class InstructionStrengthEnum(str, Enum):
    MANDATORY = "mandatory"
    RECOMMENDED_OR_QUALIFIED = "recommended_or_qualified"
    INFORMATIONAL = "informational"
    UNCLEAR = "unclear"

class CalculationStatusEnum(str, Enum):
    CALCULATED = "calculated"
    PROVISIONAL = "provisional"
    CANNOT_CALCULATE = "cannot_calculate"

class DeadlineInterpretation(BaseModel):
    """
    Transparent interpretation of an accommodation request deadline.
    Attendee support guidance only; not a legal compliance determination.
    """
    original_instruction: str = Field(..., description="Exact verified verbatim quote from document")
    page_number: int = Field(..., description="Physical PDF page number where instruction appears")
    is_verified: bool = Field(..., description="Whether evidence quote was verified against extracted text")
    instruction_strength: InstructionStrengthEnum = Field(..., description="Classification of mandatory vs qualified")
    qualifier_text: Optional[str] = Field(None, description="Explicit qualifier if present (e.g. 'if possible')")
    target_event: str = Field(..., description="The event the deadline refers to (e.g., 'City Council Meeting')")
    meeting_date_str: Optional[str] = Field(None, description="Meeting date string if established")
    meeting_time_str: Optional[str] = Field(None, description="Meeting start time string if established")
    is_past_meeting: bool = Field(default=False, description="Whether the meeting date has already passed")
    days_offset: Optional[int] = Field(None, description="Extracted numerical day or hour offset")
    offset_unit: Optional[str] = Field(None, description="'working_days', 'calendar_days', 'hours', or 'ambiguous_days'")
    calculated_date: Optional[str] = Field(None, description="Calculated date string (e.g. 'November 5, 2026')")
    calculated_time: Optional[str] = Field(None, description="Calculated time string if hour-based (e.g. '6:30 PM')")
    calculation_status: CalculationStatusEnum = Field(..., description="calculated, provisional, or cannot_calculate")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions made in the calculation")
    limitations: List[str] = Field(default_factory=list, description="Disclosed limitations and holiday uncertainties")
    explanation: str = Field(..., description="Human-readable plain language explanation")
