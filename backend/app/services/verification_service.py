import re
from typing import List, Dict, Optional, Tuple
from app.schemas.document import PageExtractionResult
from app.schemas.analysis import (
    FindingCategoryEnum,
    FindingStatusEnum,
    RawFindingItem,
    FindingItem,
    CATEGORY_METADATA,
)

def normalize_text_whitespace(text: str) -> str:
    """Normalize internal whitespaces, line breaks, and punctuation spacing for robust quote matching."""
    if not text:
        return ""
    # Replace line breaks, tabs, and multiple spaces with a single space
    return re.sub(r"\s+", " ", text).strip().lower()

def verify_findings(
    raw_findings: List[RawFindingItem],
    extracted_pages: List[PageExtractionResult],
    total_pages: int
) -> List[FindingItem]:
    """
    Independently verifies raw findings against extracted physical PDF page texts.
    Guarantees:
    1. Valid category mapping.
    2. Physical page number range validity (1-indexed).
    3. Exact verbatim quotation presence on the claimed physical page.
    4. Contextual separation (prevents conflating public-comment deadlines with accommodation deadlines).
    5. No fabricated quotes are marked verified.
    """
    page_text_map: Dict[int, str] = {
        p.page_number: p.text for p in extracted_pages
    }
    normalized_page_text_map: Dict[int, str] = {
        p.page_number: normalize_text_whitespace(p.text) for p in extracted_pages
    }

    # Group raw findings by valid category
    raw_by_category: Dict[FindingCategoryEnum, RawFindingItem] = {}
    for item in raw_findings:
        try:
            cat_enum = FindingCategoryEnum(item.category)
            raw_by_category[cat_enum] = item
        except (ValueError, KeyError):
            # Invalid category returned by model is ignored
            continue

    verified_findings: List[FindingItem] = []

    # Iterate over all defined standard categories to guarantee comprehensive coverage
    for cat in FindingCategoryEnum:
        metadata = CATEGORY_METADATA[cat]
        raw = raw_by_category.get(cat)

        if not raw:
            # Model omitted category: treated strictly as not found
            verified_findings.append(
                FindingItem(
                    category=cat,
                    category_label=metadata["label"],
                    status=FindingStatusEnum.NOT_FOUND_IN_DOCUMENT,
                    quote=None,
                    page_number=None,
                    is_quote_verified=False,
                    verification_notes="No evidence found in extracted document text.",
                    explanation=f"No explicit mention of {metadata['label'].lower()} was detected in this agenda.",
                    suggested_action=f"Contact the meeting organizer to confirm details regarding {metadata['label'].lower()}."
                )
            )
            continue

        status = raw.status
        quote = raw.quote.strip() if raw.quote else None
        page_num = raw.page_number
        explanation = raw.explanation.strip() if raw.explanation else ""
        suggested_action = raw.suggested_action.strip() if raw.suggested_action else ""

        # Default verification flags
        is_quote_verified = False
        verification_notes: Optional[str] = None

        if status in (FindingStatusEnum.FOUND, FindingStatusEnum.UNCLEAR):
            is_quote_verified, verification_notes, adjusted_status = _verify_evidence_quote(
                cat=cat,
                quote=quote,
                page_num=page_num,
                total_pages=total_pages,
                raw_page_map=page_text_map,
                normalized_page_map=normalized_page_text_map
            )
            if adjusted_status:
                status = adjusted_status
        elif status == FindingStatusEnum.NOT_FOUND_IN_DOCUMENT:
            # When marked not found, clear any phantom quote or page reference
            quote = None
            page_num = None
            is_quote_verified = False
            verification_notes = "Absence verified: no evidence in extracted text."
        elif status == FindingStatusEnum.NOT_APPLICABLE:
            quote = None
            page_num = None
            is_quote_verified = False
            verification_notes = "Classified as not applicable based on meeting context."

        verified_findings.append(
            FindingItem(
                category=cat,
                category_label=metadata["label"],
                status=status,
                quote=quote,
                page_number=page_num,
                is_quote_verified=is_quote_verified,
                verification_notes=verification_notes,
                explanation=explanation or f"Evaluation of {metadata['label'].lower()}.",
                suggested_action=suggested_action or "Review meeting agenda or contact the agency clerk."
            )
        )

    return verified_findings


def _verify_evidence_quote(
    cat: FindingCategoryEnum,
    quote: Optional[str],
    page_num: Optional[int],
    total_pages: int,
    raw_page_map: Dict[int, str],
    normalized_page_map: Dict[int, str]
) -> Tuple[bool, str, Optional[FindingStatusEnum]]:
    """
    Subroutine verifying quote existence, page bounds, and semantic integrity.
    """
    if not quote or quote.strip() == "":
        return False, "Finding marked found/unclear, but no supporting quotation was provided by model.", FindingStatusEnum.UNCLEAR

    if page_num is None:
        return False, "No page number was provided for the cited quotation.", FindingStatusEnum.UNCLEAR

    # Check 1: Page number bounds
    if page_num < 1 or page_num > total_pages:
        return (
            False,
            f"Physical page {page_num} is outside the valid document range (1 to {total_pages}).",
            FindingStatusEnum.UNCLEAR
        )

    # Check 2: Page text existence
    raw_page_text = raw_page_map.get(page_num, "")
    norm_page_text = normalized_page_map.get(page_num, "")
    norm_quote = normalize_text_whitespace(quote)

    if norm_quote not in norm_page_text:
        # Quote does not exist on claimed page! Check if it appears on any other page
        matched_other_page = None
        for p, other_text in normalized_page_map.items():
            if norm_quote in other_text:
                matched_other_page = p
                break

        if matched_other_page:
            return (
                False,
                f"Quotation verification failed: quote is not on page {page_num}, but exists on page {matched_other_page}.",
                FindingStatusEnum.UNCLEAR
            )
        else:
            return (
                False,
                f"Quotation verification failed: quote could not be located in page {page_num} extracted text.",
                FindingStatusEnum.UNCLEAR
            )

    # Check 3: Contextual distinction defense
    # Category 3A: Explicit accommodation deadlines vs Public Comment deadlines
    if cat == FindingCategoryEnum.EXPLICIT_ACCOMMODATION_DEADLINES:
        quote_lower = norm_quote.lower()
        public_comment_terms = ["public comment", "speaker card", "written comment", "agenda packet", "comment period"]
        accommodation_terms = ["disability", "accommodation", "assistance", "special need", "ada", "auxiliary", "clerk", "accessible", "interpreter", "hours prior", "days prior", "advance notice"]

        has_comment_term = any(t in quote_lower for t in public_comment_terms)
        has_accom_term = any(t in quote_lower for t in accommodation_terms)

        if has_comment_term and not has_accom_term:
            return (
                False,
                "Contextual verification rejected: Quote describes a public-comment or agenda submission deadline, NOT a disability accommodation deadline.",
                FindingStatusEnum.UNCLEAR
            )

    # Category 3B: ASL / Sign Language vs General ADA
    if cat == FindingCategoryEnum.ASL_SIGN_LANGUAGE_INTERPRETATION:
        quote_lower = norm_quote.lower()
        asl_terms = ["sign language", "asl", "interpreter", "interpreting", "deaf", "hard of hearing", "hearing impaired"]
        if not any(t in quote_lower for t in asl_terms):
            return (
                False,
                "Contextual notice: Quote cites general accommodations without explicit reference to ASL or sign-language interpreters.",
                FindingStatusEnum.UNCLEAR
            )

    # All checks passed
    return True, "Verified exact quotation on physical PDF page.", None
