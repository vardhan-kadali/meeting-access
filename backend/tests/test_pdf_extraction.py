import io
import pytest
from httpx import AsyncClient, ASGITransport
import pypdf
from app.main import app

def generate_pdf_with_text(pages_text: list[str]) -> bytes:
    """
    Generates a valid, minimal multi-page PDF in memory containing specific text lines.
    """
    kids_refs = " ".join(f"{i + 3} 0 R" for i in range(len(pages_text)))
    num_pages = len(pages_text)

    body_objects = []
    # 1: Catalog
    body_objects.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
    # 2: Pages
    body_objects.append(f"2 0 obj << /Type /Pages /Kids [{kids_refs}] /Count {num_pages} >> endobj")

    # Font object ID: 3 + num_pages
    font_id = 3 + num_pages
    # Contents object IDs start at font_id + 1

    # Page objects
    for i in range(num_pages):
        page_id = 3 + i
        contents_id = font_id + 1 + i
        body_objects.append(
            f"{page_id} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {contents_id} 0 R >> endobj"
        )

    # Font object
    body_objects.append(f"{font_id} 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")

    # Stream contents
    for i, text in enumerate(pages_text):
        contents_id = font_id + 1 + i
        # Safe escape for parentheses
        safe_text = text.replace("(", "\\(").replace(")", "\\)")
        # In PDF: 72pt margins
        stream_data = f"BT /F1 12 Tf 72 712 Td ({safe_text}) Tj ET"
        body_objects.append(
            f"{contents_id} 0 obj << /Length {len(stream_data)} >> stream\n{stream_data}\nendstream endobj"
        )

    # Calculate xref offsets
    output = "%PDF-1.4\n"
    offsets = [0]
    for obj in body_objects:
        offsets.append(len(output.encode("latin1")))
        output += obj + "\n"

    xref_offset = len(output.encode("latin1"))
    total_objects = len(offsets)

    output += f"xref\n0 {total_objects}\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        output += f"{offset:010d} 00000 n \n"

    output += f"trailer << /Size {total_objects} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    return output.encode("latin1")


def generate_blank_pdf(num_pages: int) -> bytes:
    writer = pypdf.PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def generate_encrypted_pdf(password: str) -> bytes:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt(password)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.mark.anyio
async def test_valid_multipage_pdf_extraction():
    """Verify multi-page PDF extraction, 1-based page numbers, and exact text retention."""
    pages = [
        "City of Claremont City Council Meeting Agenda Nov 10, 2026. General accessibility information.",
        "Disability accommodations: Contact the City Clerk at least 72 hours prior to the meeting.",
        "Public comment instructions: Speakers may submit written comments up to 3:00 PM."
    ]
    pdf_bytes = generate_pdf_with_text(pages)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("agenda.pdf", pdf_bytes, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "agenda.pdf"
    assert data["total_pages"] == 3
    assert data["overall_status"] == "text_extracted"
    assert data["ocr_warning"] is None
    assert len(data["pages"]) == 3

    for idx, p in enumerate(data["pages"]):
        assert p["page_number"] == idx + 1  # 1-based physical page number
        assert pages[idx] in p["text"]
        assert p["char_count"] > 0
        assert p["status"] == "text_extracted"


@pytest.mark.anyio
async def test_empty_upload_rejected():
    """Empty files (0 bytes) must be rejected with 400 Bad Request."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_non_pdf_extension_rejected():
    """Non-PDF extension must be rejected with 400 Bad Request."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("document.txt", b"Hello world", "text/plain")}
        )
    assert response.status_code == 400
    assert "extension" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_fake_pdf_signature_rejected():
    """A file named .pdf containing arbitrary text lacking %PDF- must be rejected with 400."""
    fake_bytes = b"This is a plain text file pretending to be a PDF document."
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("fake.pdf", fake_bytes, "application/pdf")}
        )
    assert response.status_code == 400
    assert "%PDF-" in response.json()["detail"]


@pytest.mark.anyio
async def test_corrupted_pdf_rejected():
    """A file with %PDF- header but broken internal structure must be rejected safely with 400."""
    corrupted_bytes = b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> ... truncated garbage"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("corrupted.pdf", corrupted_bytes, "application/pdf")}
        )
    assert response.status_code == 400
    assert "unreadable" in response.json()["detail"].lower() or "malformed" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_encrypted_pdf_rejected():
    """Password-protected PDFs must be rejected with 422 Unprocessable Entity."""
    encrypted_bytes = generate_encrypted_pdf("pass123")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("encrypted.pdf", encrypted_bytes, "application/pdf")}
        )
    assert response.status_code == 422
    assert "encrypted" in response.json()["detail"].lower() or "password" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_no_extractable_text_detection():
    """A blank or image-only PDF should return no_extractable_text and an informative OCR warning."""
    blank_bytes = generate_blank_pdf(2)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("scanned_blank.pdf", blank_bytes, "application/pdf")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total_pages"] == 2
    assert data["overall_status"] == "no_extractable_text"
    assert data["ocr_warning"] is not None
    assert "OCR" in data["ocr_warning"]
    for p in data["pages"]:
        assert p["char_count"] == 0
        assert p["status"] == "empty_or_image"


@pytest.mark.anyio
async def test_partially_extracted_detection():
    """A document with some text pages and some blank pages is flagged as partially_extracted."""
    # 2 text pages (long enough to qualify as text_extracted), 1 blank page
    long_text = "This is a comprehensive public meeting agenda notice with detailed accessibility and accommodation text. " * 3
    pdf_bytes = generate_pdf_with_text([long_text, long_text, ""])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("partial.pdf", pdf_bytes, "application/pdf")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total_pages"] == 3
    assert data["overall_status"] == "partially_extracted"
    assert data["pages"][0]["status"] == "text_extracted"
    assert data["pages"][1]["status"] == "text_extracted"
    assert data["pages"][2]["status"] == "empty_or_image"


@pytest.mark.anyio
async def test_upload_size_limit_exceeded(monkeypatch):
    """File size exceeding MAX_UPLOAD_SIZE_MB must return 413."""
    # Temporarily set MAX_UPLOAD_SIZE_MB to 1MB for testing
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

    # 1.5 MB dummy content with %PDF- header
    large_bytes = b"%PDF-1.4\n" + b"A" * (int(1.5 * 1024 * 1024))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("oversized.pdf", large_bytes, "application/pdf")}
        )
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_page_count_limit_exceeded(monkeypatch):
    """PDF exceeding MAX_PAGE_COUNT must return 413."""
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_PAGE_COUNT", 3)

    # Generate 4-page blank PDF
    four_page_bytes = generate_blank_pdf(4)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/extract",
            files={"file": ("many_pages.pdf", four_page_bytes, "application/pdf")}
        )
    assert response.status_code == 413
    assert "exceeds maximum page limit" in response.json()["detail"].lower()
