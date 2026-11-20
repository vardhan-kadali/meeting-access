import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, call
from google.genai.errors import ServerError, ClientError

from app.main import app
from app.config import settings
from app.schemas.analysis import FindingCategoryEnum, FindingStatusEnum
from app.schemas.deadline import InstructionStrengthEnum
from tests.test_pdf_extraction import generate_pdf_with_text


def make_standard_mock_findings(deadline_quote="least three (3) working days prior to the meeting, if possible", deadline_page=1):
    return {
        "findings": [
            {
                "category": "disability_accommodation_contact",
                "status": "found",
                "quote": "contact City Clerk at 909-399-5460",
                "page_number": 1,
                "explanation": "City Clerk contact provided.",
                "suggested_action": "Contact the City Clerk."
            },
            {
                "category": "accommodation_request_methods",
                "status": "found",
                "quote": "contact City Clerk at 909-399-5460",
                "page_number": 1,
                "explanation": "Procedures provided.",
                "suggested_action": "Call or email."
            },
            {
                "category": "explicit_accommodation_deadlines",
                "status": "found",
                "quote": deadline_quote,
                "page_number": deadline_page,
                "explanation": "Advance notice timeframe provided.",
                "suggested_action": "Notify clerk in advance."
            },
            {
                "category": "alternative_document_formats",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "Not mentioned.",
                "suggested_action": "Inquire if needed."
            },
            {
                "category": "asl_sign_language_interpretation",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "No ASL info in document.",
                "suggested_action": "Request interpreter."
            },
            {
                "category": "live_captioning",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "No captioning info.",
                "suggested_action": "Contact clerk."
            },
            {
                "category": "assisted_listening_devices",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "Not listed.",
                "suggested_action": "Contact clerk."
            },
            {
                "category": "remote_participation_instructions",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "None provided.",
                "suggested_action": "Attend in person."
            },
            {
                "category": "public_comment_instructions",
                "status": "not_found_in_document",
                "quote": None,
                "page_number": None,
                "explanation": "Not specified.",
                "suggested_action": "Review agenda."
            }
        ]
    }


def sample_pdf_content():
    return generate_pdf_with_text([
        "City of Claremont City Council Meeting Agenda Tuesday, November 10, 2026 at 6:30 PM. "
        "For disability accommodations, contact City Clerk at 909-399-5460 at least three (3) working days prior to the meeting, if possible."
    ])


# 1. Primary Model Succeeds Without Fallback
@pytest.mark.anyio
async def test_primary_model_succeeds_without_fallback():
    """Primary model (gemini-3.8-flash) succeeds on first attempt; model_used recorded properly."""
    pdf_bytes = sample_pdf_content()
    mock_response = MagicMock()
    mock_response.text = json.dumps(make_standard_mock_findings())

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["model_used"] == "gemini-3.8-flash"
    assert mock_client.models.generate_content.call_count == 1
    call_kwargs = mock_client.models.generate_content.call_args[1]
    assert call_kwargs["model"] == "gemini-3.8-flash"


# 2. Primary 503 -> Fallback Succeeds
@pytest.mark.anyio
async def test_primary_503_fallback_succeeds():
    """Primary model returns 503 on all retries, fallback model (gemini-3.5-flash-lite) succeeds."""
    pdf_bytes = sample_pdf_content()
    mock_success = MagicMock()
    mock_success.text = json.dumps(make_standard_mock_findings())

    server_error = ServerError(
        503,
        {"error": {"code": 503, "message": "Model is experiencing high demand."}},
        MagicMock()
    )

    mock_client = MagicMock()
    # Primary attempts 1 and 2 fail with 503; Fallback attempt 1 succeeds
    mock_client.models.generate_content.side_effect = [
        server_error,
        server_error,
        mock_success
    ]

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["model_used"] == "gemini-3.5-flash-lite"
    assert mock_client.models.generate_content.call_count == 3


# 3. Primary Exhausts Retries Before Switching to Fallback
@pytest.mark.anyio
async def test_primary_exhausts_retries_before_fallback():
    """Verify primary model exhausts all retries (MAX_RETRIES_PER_MODEL) before fallback is called."""
    pdf_bytes = sample_pdf_content()
    mock_success = MagicMock()
    mock_success.text = json.dumps(make_standard_mock_findings())

    server_error = ServerError(
        503,
        {"error": {"code": 503, "message": "Temporary capacity overload."}},
        MagicMock()
    )

    models_called = []

    def mock_generate_content(*args, **kwargs):
        model = kwargs.get("model")
        models_called.append(model)
        if model == "gemini-3.8-flash":
            raise server_error
        return mock_success

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = mock_generate_content

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    assert resp.json()["model_used"] == "gemini-3.5-flash-lite"
    assert models_called == [
        "gemini-3.8-flash",
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]


# 4. Both Models Fail with Controlled 503
@pytest.mark.anyio
async def test_both_models_fail_controlled_503():
    """When both primary and fallback models fail with 503, raises clean HTTP 503 with standardized message."""
    pdf_bytes = sample_pdf_content()
    server_error = ServerError(
        503,
        {"error": {"code": 503, "message": "Unavailable."}},
        MagicMock()
    )

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = server_error

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert "All configured AI analysis models are currently unavailable" in detail
    # 2 retries on primary + 2 retries on fallback = 4 calls total
    assert mock_client.models.generate_content.call_count == 4


# 5. Authentication Failure: No Retry, No Fallback
@pytest.mark.anyio
async def test_authentication_failure_no_retry_no_fallback():
    """Authentication errors (401/403) immediately fail with 401 without retry or fallback."""
    pdf_bytes = sample_pdf_content()
    auth_error = ClientError(
        401,
        {"error": {"code": 401, "message": "API key not valid. Please pass a valid API key."}},
        MagicMock()
    )

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = auth_error

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 401
    assert "authentication failed" in resp.json()["detail"].lower()
    # Must immediately abort after 1 call
    assert mock_client.models.generate_content.call_count == 1


# 6. Quota/Billing 429: No Retry, No Fallback
@pytest.mark.anyio
async def test_quota_billing_429_handled_appropriately():
    """Account quota/billing exhaustion immediately fails with 429 without retry or fallback."""
    pdf_bytes = sample_pdf_content()
    quota_error = ClientError(
        429,
        {"error": {"code": 429, "message": "Resource has been exhausted: check quota or billing settings for project."}},
        MagicMock()
    )

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = quota_error

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 429
    assert "quota or billing limit exceeded" in resp.json()["detail"].lower()
    # Must immediately abort after 1 call
    assert mock_client.models.generate_content.call_count == 1


# 7. Invalid Model Configuration (404) Handled
@pytest.mark.anyio
async def test_invalid_model_configuration_handled():
    """404 Not Found on invalid model immediately skips retries and tries next fallback model."""
    pdf_bytes = sample_pdf_content()
    not_found_error = ClientError(
        404,
        {"error": {"code": 404, "message": "models/gemini-invalid is not found for API version v1beta"}},
        MagicMock()
    )
    mock_success = MagicMock()
    mock_success.text = json.dumps(make_standard_mock_findings())

    models_called = []

    def mock_generate_content(*args, **kwargs):
        model = kwargs.get("model")
        models_called.append(model)
        if model == "gemini-3.8-flash":
            raise not_found_error
        return mock_success

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = mock_generate_content

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    assert resp.json()["model_used"] == "gemini-3.5-flash-lite"
    # Primary was called ONCE (no retries on 404), fallback was called ONCE and succeeded
    assert models_called == ["gemini-3.8-flash", "gemini-3.5-flash-lite"]


# 8. Fallback Output Passes Strict Evidence Verification
@pytest.mark.anyio
async def test_fallback_output_passes_evidence_verification():
    """Outputs from the fallback model undergo identical strict Python evidence verification."""
    pdf_bytes = sample_pdf_content()

    mock_findings = make_standard_mock_findings()
    # Intentionally inject a hallucinated quote into ASL finding to verify verification runs
    mock_findings["findings"][4] = {
        "category": "asl_sign_language_interpretation",
        "status": "found",
        "quote": "Hallucinated ASL interpreter notice not on page",
        "page_number": 1,
        "explanation": "Fake ASL claim.",
        "suggested_action": "Request interpreter."
    }

    mock_success = MagicMock()
    mock_success.text = json.dumps(mock_findings)

    server_error = ServerError(503, {"error": {"code": 503, "message": "Capacity"}}, MagicMock())

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        server_error,
        server_error,
        mock_success
    ]

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["model_used"] == "gemini-3.5-flash-lite"

    contact = next(f for f in data["findings"] if f["category"] == "disability_accommodation_contact")
    assert contact["is_quote_verified"] is True
    assert "Verified exact quotation" in contact["verification_notes"]

    asl = next(f for f in data["findings"] if f["category"] == "asl_sign_language_interpretation")
    assert asl["is_quote_verified"] is False
    assert "could not be located" in asl["verification_notes"]


# 9. Deadline Interpretation Preserved on Fallback
@pytest.mark.anyio
async def test_deadline_interpretation_preserved_on_fallback():
    """Deadline interpretation engine functions seamlessly when results originate from fallback model."""
    pdf_bytes = sample_pdf_content()
    mock_success = MagicMock()
    mock_success.text = json.dumps(make_standard_mock_findings(
        deadline_quote="least three (3) working days prior to the meeting, if possible",
        deadline_page=1
    ))

    server_error = ServerError(503, {"error": {"code": 503, "message": "Capacity"}}, MagicMock())

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        server_error,
        server_error,
        mock_success
    ]

    with patch("google.genai.Client", return_value=mock_client), patch("time.sleep", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/documents/analyze",
                files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["model_used"] == "gemini-3.5-flash-lite"

    interp = data["deadline_interpretation"]
    assert interp is not None
    assert interp["calculated_date"] == "November 05, 2026"
    assert interp["instruction_strength"] == "recommended_or_qualified"
    assert interp["qualifier_text"] == "if possible"
    assert interp["days_offset"] == 3
    assert interp["offset_unit"] == "working_days"
    assert any("holiday" in lim.lower() for lim in interp["limitations"])
