import sys
import json
import asyncio
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

import httpx
from app.main import app

async def run_live_smoke_test():
    official_pdf_path = backend_dir.parent / "sample_data" / "11-10-26-city-council-agenda-only.pdf"
    if not official_pdf_path.exists():
        print(f"Official PDF not found at {official_pdf_path}")
        return

    with open(official_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"Executing Live Smoke Test with AUTHENTIC agenda: {official_pdf_path.name} ({len(pdf_bytes)} bytes)...")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=90.0) as client:
        response = await client.post(
            "/api/documents/analyze",
            files={"file": (official_pdf_path.name, pdf_bytes, "application/pdf")}
        )

    print(f"Response HTTP Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\n--- ANALYSIS SUMMARY ---")
        print(f"Filename: {data['filename']}")
        print(f"Model: {data['model_used']}")
        print(f"Total Pages: {data['total_pages']}")
        print(f"Verified Evidence Items: {data['verified_evidence_count']}")
        print(f"Unclear Items: {data['unclear_evidence_count']}")
        print(f"Missing Items: {data['missing_evidence_count']}")

        print("\n--- DEADLINE INTERPRETATION (MILESTONE 4) ---")
        deadline = data.get("deadline_interpretation")
        if deadline:
            print(f"Original Instruction (P.{deadline['page_number']}): \"{deadline['original_instruction']}\"")
            print(f"Instruction Strength: {deadline['instruction_strength'].upper()}")
            print(f"Qualifier Text: {deadline['qualifier_text']}")
            print(f"Target Event: {deadline['target_event']}")
            print(f"Meeting Date: {deadline['meeting_date_str']} (Time: {deadline['meeting_time_str']})")
            print(f"Is Past Meeting: {deadline['is_past_meeting']}")
            print(f"Calculated Date: {deadline['calculated_date']}")
            print(f"Calculation Status: {deadline['calculation_status'].upper()}")
            print(f"Assumptions:")
            for a in deadline['assumptions']:
                print(f"  - {a}")
            print(f"Disclosed Limitations & Holiday Uncertainty:")
            for lim in deadline['limitations']:
                print(f"  - {lim}")
            print(f"Explanation: {deadline['explanation']}")
        else:
            print("No deadline interpretation returned.")

        print("\n--- DETAILED CATEGORY FINDINGS ---")
        for finding in data["findings"]:
            v_badge = "VERIFIED" if finding["is_quote_verified"] else "UNVERIFIED"
            print(f"\n* [{finding['category_label']}]")
            print(f"  Status: {finding['status'].upper()} ({v_badge})")
            if finding["quote"]:
                print(f"  Quote (Page {finding['page_number']}): \"{finding['quote']}\"")
                print(f"  Verification Note: {finding['verification_notes']}")
            print(f"  Explanation: {finding['explanation']}")
            print(f"  Suggested Action: {finding['suggested_action']}")
    else:
        print("API Error Output:", response.text)

if __name__ == "__main__":
    asyncio.run(run_live_smoke_test())
