"""
Backend Tests
Run: pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ─────────────────────────────────────────
# Health & Root
# ─────────────────────────────────────────

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "running" in res.json()["message"].lower()


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


# ─────────────────────────────────────────
# Text Analysis
# ─────────────────────────────────────────

SCAM_TEXT = """
URGENT HIRING! Earn 50,000 per day from home! No experience needed.
Registration fee 500 rupees only. Send Aadhar card and bank account details.
WhatsApp ONLY. HURRY! Only 10 seats left! 100% guaranteed income!
"""

LEGIT_TEXT = """
We are an IT company looking for a Python Developer with 2+ years of experience.
The role involves building REST APIs. Salary: 8-12 LPA. Apply through our portal.
Interview process includes technical and HR rounds. Company email: hr@techcorp.com.
Location: Bangalore (Hybrid). PF and health insurance provided.
"""

SUSPICIOUS_TEXT = """
Work from home opportunity. Earn 25000-50000 per month. Data entry work.
No experience needed. Training provided. Contact on WhatsApp for details.
Flexible hours. Limited slots available.
"""


def test_analyze_scam_text():
    res = client.post("/analyze/text", json={"text": SCAM_TEXT})
    assert res.status_code == 200
    data = res.json()
    assert data["label"] in ["SUSPICIOUS", "SCAM"]
    assert data["score"] > 40
    assert len(data["reasons"]) > 0
    assert "score" in data
    assert "confidence" in data


def test_analyze_legit_text():
    res = client.post("/analyze/text", json={"text": LEGIT_TEXT})
    assert res.status_code == 200
    data = res.json()
    assert data["label"] in ["LEGITIMATE", "SUSPICIOUS"]
    assert data["score"] < 70


def test_analyze_suspicious_text():
    res = client.post("/analyze/text", json={"text": SUSPICIOUS_TEXT})
    assert res.status_code == 200
    data = res.json()
    assert data["label"] in ["SUSPICIOUS", "SCAM"]


def test_analyze_short_text_rejected():
    res = client.post("/analyze/text", json={"text": "hire me"})
    assert res.status_code == 400


def test_analyze_returns_all_fields():
    res = client.post("/analyze/text", json={"text": SCAM_TEXT})
    data = res.json()
    required_fields = [
        "label", "score", "confidence", "reasons",
        "highlighted_keywords", "ml_probability",
        "rule_penalty", "feature_breakdown"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


# ─────────────────────────────────────────
# URL Analysis
# ─────────────────────────────────────────

def test_analyze_invalid_url():
    res = client.post("/analyze/url", json={"url": "not-a-url"})
    assert res.status_code == 400


# ─────────────────────────────────────────
# Feature Extractor Unit Tests
# ─────────────────────────────────────────

from utils.feature_extractor import extract_all_features, get_risky_keywords
from utils.scorer import compute_scam_score
from utils.preprocessor import preprocess_text


def test_scam_features_detected():
    text = "registration fee required. send aadhar. whatsapp only. earn 1 lakh daily."
    features = extract_all_features(text)
    assert features["asks_for_fee"] is True
    assert features["asks_for_documents"] is True
    assert features["whatsapp_contact"] is True
    assert features["salary_too_high"] is True


def test_legit_features():
    text = "python developer role. salary 10 lpa. apply via company portal. hr@company.com"
    features = extract_all_features(text)
    assert features["asks_for_fee"] is False
    assert features["whatsapp_contact"] is False


def test_risky_keywords_found():
    text = "urgent hiring! guaranteed income. registration fee required. no experience needed."
    kws = get_risky_keywords(text)
    assert len(kws) > 0
    assert any("registration fee" in k for k in kws)


def test_scam_score_high_for_scam():
    features = {
        "asks_for_fee": True,
        "asks_for_documents": True,
        "whatsapp_contact": True,
        "salary_too_high": True,
        "guaranteed_language": True,
        "uses_free_email": True,
        "no_experience_claim": True,
        "high_risk_pattern_count": 5,
        "urgency_score": 4,
        "domain_age_days": 10,
        "has_ssl": 0,
        "platform_trust_score": 0.2,
        "caps_ratio": 0.3,
        "telegram_contact": False,
        "has_company_name": False,
        "has_location": False,
        "has_job_requirements": False,
        "legit_signal_count": 0,
        "is_known_platform": False,
        "uses_company_email": False,
        "has_company_description": False,
    }
    result = compute_scam_score(0.9, features)
    assert result["label"] == "SCAM"
    assert result["score"] >= 70


def test_scam_score_low_for_legit():
    features = {
        "asks_for_fee": False,
        "asks_for_documents": False,
        "whatsapp_contact": False,
        "salary_too_high": False,
        "guaranteed_language": False,
        "uses_free_email": False,
        "no_experience_claim": False,
        "high_risk_pattern_count": 0,
        "urgency_score": 0,
        "domain_age_days": 1000,
        "has_ssl": 1,
        "platform_trust_score": 0.9,
        "caps_ratio": 0.02,
        "telegram_contact": False,
        "has_company_name": True,
        "has_location": True,
        "has_job_requirements": True,
        "legit_signal_count": 4,
        "is_known_platform": True,
        "uses_company_email": True,
        "has_company_description": True,
    }
    result = compute_scam_score(0.05, features)
    assert result["label"] == "LEGITIMATE"
    assert result["score"] < 40


def test_preprocessor():
    raw = "URGENT!!! Visit http://scam.com for INFO. Email: fake@gmail.com"
    result = preprocess_text(raw)
    assert "URLTOKEN" in result["cleaned_text"]
    assert "EMAILTOKEN" in result["cleaned_text"]
    assert result["exclamation_count"] == 3
    assert result["caps_ratio"] > 0
    assert "fake@gmail.com" in result["emails_found"]
