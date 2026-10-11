"""Automated Smoke Test Suite for Zari Travel Platform."""

import sys
from fastapi.testclient import TestClient

from main import app
from hotel_database import db_session, save_lead


def run_tests():
    print("=" * 60)
    print("Zari Travel Autonomous Platform - Smoke Test Suite")
    print("=" * 60)
    client = TestClient(app)
    passed = 0
    total = 3

    # ── Test 1: Headers, CSP and Static Assets ──────────────────────────────
    print("\n[TEST 1] Testing Root Route (/) and Security Headers...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    
    csp = res.headers.get("Content-Security-Policy", "")
    assert "https://prod.spline.design" in csp, "CSP missing Spline permission"
    assert "https://fonts.googleapis.com" in csp, "CSP missing Google Fonts permission"
    assert res.headers.get("X-Frame-Options") == "DENY", "Missing X-Frame-Options"
    
    # Check favicon.svg static delivery
    fav_res = client.get("/static/favicon.svg")
    assert fav_res.status_code == 200, f"Favicon delivery failed: {fav_res.status_code}"
    print("[OK] Test 1 Passed: Root 200, CSP with Spline rules, X-Frame-Options, Favicon available.")
    passed += 1

    # ── Test 2: Conversational AI Agent Fallback & Reliability ──────────────
    print("\n[TEST 2] Testing Chat Agent (/api/agent/chat)...")
    chat_payload = {
        "message": "Ищу тур в Дубай на двоих",
        "session_id": "test_smoke_session_1",
        "lang": "ru"
    }
    chat_res = client.post("/api/agent/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat returned {chat_res.status_code}"
    data = chat_res.json()
    assert "reply" in data, "Response missing reply"
    assert "state" in data, "Response missing state"
    assert data["state"] in ("COMPLETE", "INCOMPLETE", "BUDGET_MISMATCH"), f"Invalid state {data['state']}"
    print(f"[OK] Test 2 Passed: Chat agent responded with state='{data['state']}' without exceptions.")
    passed += 1

    # ── Test 3: Leads Pipeline (SQLite persistence & endpoint) ──────────────
    print("\n[TEST 3] Testing Leads Booking Pipeline & SQLite storage...")
    lead_payload = {
        "client_name": "Test Client",
        "client_phone": "+7 701 999 88 77",
        "client_comment": "Testing booking persistence",
        "hotel_name": "Burj Al Arab Jumeirah",
        "destination": "UAE",
        "dates": "2026-10-20 - 2026-10-27",
        "flight_info": "Air Astana KC 897",
        "meal_plan": "BB",
        "room_category": "Deluxe Marina Suite",
        "total_price_kzt": 2500000,
        "total_price_usd": 5000
    }
    lead_res = client.post("/api/leads", json=lead_payload)
    assert lead_res.status_code == 200, f"Leads endpoint returned {lead_res.status_code}"
    lead_data = lead_res.json()
    assert lead_data.get("status") == "success", "Lead creation status not success"
    created_id = lead_data.get("lead_id")
    assert created_id and created_id > 0, "Invalid lead_id returned"

    # Verify directly from database
    with db_session() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (created_id,)).fetchone()
        assert row is not None, f"Lead #{created_id} not found in SQLite table 'leads'"
        assert row["client_name"] == "Test Client"
        assert row["total_price_kzt"] == 2500000
    
    print(f"[OK] Test 3 Passed: Lead #{created_id} created and verified in SQLite 'leads' table.")
    passed += 1

    # ── Test 4: Weeks & Multi-token Date Extraction ──────────────────────────
    print("\n[TEST 4] Testing '1 week' / 'на неделю' parsing and date extraction...")
    from ai_agent import _extract_nights, _extract_date
    assert _extract_nights("на неделю") == 7, "Failed: 'на неделю' should be 7 nights"
    assert _extract_nights("1 week") == 7, "Failed: '1 week' should be 7 nights"
    assert _extract_nights("на 2 недели") == 14, "Failed: 'на 2 недели' should be 14 nights"
    d = _extract_date("Тур в Дубай на 7 ночей, вылет 20 октября, двое взрослых")
    assert d == "2026-10-20", f"Failed: expected '2026-10-20', got '{d}'"
    print("[OK] Test 4 Passed: Week extraction (7, 14 nights) and date parsing verified.")
    passed += 1

    # ── Test 5: Strict Budget Filter Enforcement ─────────────────────────────
    print("\n[TEST 5] Testing Strict Budget Filter (no overpriced hotels dumped)...")
    budget_payload = {
        "message": "Тур в Дубай на 7 ночей, вылет 20 октября, двое взрослых, бюджет до 1 млн тенге",
        "session_id": "test_strict_budget_session",
        "lang": "ru"
    }
    budget_res = client.post("/api/agent/chat", json=budget_payload)
    assert budget_res.status_code == 200, f"Chat returned {budget_res.status_code}"
    b_data = budget_res.json()
    assert b_data["state"] == "BUDGET_MISMATCH", f"Expected BUDGET_MISMATCH, got '{b_data['state']}'"
    assert len(b_data.get("results", [])) == 0, f"Expected 0 results for 1M KZT budget in Dubai, got {len(b_data.get('results', []))}"
    assert "минимальная стоимость" in b_data["reply"].lower(), "Reply should politely explain minimum price"
    print("[OK] Test 5 Passed: Strict budget enforced, BUDGET_MISMATCH returned with polite alternative suggestions.")
    passed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total + 2} TESTS PASSED [ALL PASS]")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
