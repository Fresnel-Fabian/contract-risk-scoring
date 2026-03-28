"""
pytest test suite — 15 tests covering all endpoints.

Run:  pytest tests/ -v
"""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

HIGH_RISK = """
SOFTWARE AS A SERVICE AGREEMENT
This Agreement is between TechVendor Inc. and Customer Corp.
All IP created under this Agreement shall be assigned to Vendor.
Vendor's liability shall not be limited or capped under any circumstances.
The agreement auto-renews annually unless terminated with 90 days prior notice.
Customer agrees to a non-compete for 24 months post-termination.
Liquidated damages of $500,000 apply for any breach.
Change of control of Customer requires Vendor consent.
Source code held in escrow.
"""

LOW_RISK = """
NON-DISCLOSURE AGREEMENT
This Agreement is entered into as of January 1, 2026 between Party A and Party B.
Both parties agree to keep all disclosed information strictly confidential.
Governed by Delaware law. Term is two years.
Either party may terminate with 30 days written notice.
"""


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    b = r.json()
    assert b["status"] == "ok"
    assert b["model_loaded"] is True
    assert b["model_type"] in ("roberta-qa", "lr-tfidf-fallback")
    assert "version" in b


# ── /clauses ──────────────────────────────────────────────────────────────────

def test_clauses_count():
    r = client.get("/clauses")
    assert r.status_code == 200
    assert r.json()["total"] == 41
    assert len(r.json()["clauses"]) == 41

def test_clauses_sorted_desc():
    weights = [c["risk_weight"] for c in client.get("/clauses").json()["clauses"]]
    assert weights == sorted(weights, reverse=True)

def test_clauses_fields():
    for c in client.get("/clauses").json()["clauses"]:
        assert {"name", "risk_weight", "description"} <= set(c)
        assert 1 <= c["risk_weight"] <= 10

def test_uncapped_liability_weight_is_10():
    clauses = {c["name"]: c for c in client.get("/clauses").json()["clauses"]}
    assert clauses["Uncapped Liability"]["risk_weight"] == 10


# ── /analyze ─────────────────────────────────────────────────────────────────

def test_analyze_returns_200():
    r = client.post("/analyze", json={"text": HIGH_RISK})
    assert r.status_code == 200

def test_analyze_score_range():
    r = client.post("/analyze", json={"text": HIGH_RISK})
    assert 0 <= r.json()["score"] <= 100

def test_analyze_high_risk_not_autoclear():
    r = client.post("/analyze", json={"text": HIGH_RISK})
    assert r.json()["triage"] in ("FLAG FOR REVIEW", "URGENT REVIEW")

def test_analyze_low_risk_not_urgent():
    r = client.post("/analyze", json={"text": LOW_RISK})
    assert r.json()["triage"] in ("AUTO-CLEAR", "FLAG FOR REVIEW")

def test_analyze_clauses_sorted():
    clauses = client.post("/analyze", json={"text": HIGH_RISK}).json()["clauses"]
    if len(clauses) >= 2:
        scores = [c["risk_weight"] * c["confidence"] for c in clauses]
        assert scores == sorted(scores, reverse=True)

def test_analyze_custom_threshold():
    r = client.post("/analyze", json={"text": HIGH_RISK, "threshold": 0.05})
    assert r.status_code == 200
    assert r.json()["threshold"] == pytest.approx(0.05)

def test_analyze_word_count():
    text = "word " * 100
    r = client.post("/analyze", json={"text": text.strip()})
    assert r.status_code == 200
    assert r.json()["word_count"] == 100

def test_analyze_model_field():
    r = client.post("/analyze", json={"text": HIGH_RISK})
    assert len(r.json()["model"]) > 0

def test_analyze_empty_text_422():
    assert client.post("/analyze", json={"text": ""}).status_code == 422

def test_analyze_missing_text_422():
    assert client.post("/analyze", json={}).status_code == 422

def test_timing_header():
    r = client.post("/analyze", json={"text": HIGH_RISK})
    assert "X-Process-Time-Ms" in r.headers

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "docs" in r.json()
