"""
Feature Extraction Engine
Extracts NLP, structural, metadata, and pattern-based features
from preprocessed job posting text.
"""

import re
from typing import Optional


# ─────────────────────────────────────────
# Scam Signal Dictionaries
# ─────────────────────────────────────────

URGENCY_PHRASES = [
    "urgent", "urgently", "immediately", "asap", "as soon as possible",
    "hurry", "limited seats", "limited slots", "apply now", "last chance",
    "closing soon", "don't miss", "do not miss", "final call",
    "today only", "this week only", "seats filling fast"
]

HIGH_RISK_PATTERNS = [
    "registration fee", "pay to apply", "pay to join", "security deposit",
    "training fee", "processing fee", "joining fee", "application fee",
    "refundable deposit", "advance payment", "pay before joining",
    "guaranteed income", "guaranteed job", "100% placement",
    "earn from home", "work from home earn", "earn daily",
    "earn weekly", "earn 50000 daily", "earn lakhs",
    "no experience needed", "no qualification required",
    "just share your details", "send your aadhar", "send your pan",
    "bank account details required", "share personal documents",
    "whatsapp only", "contact on whatsapp", "chat on whatsapp",
    "no interview required", "direct joining", "on the spot offer"
]

MEDIUM_RISK_PATTERNS = [
    "work from home", "part time", "flexible hours",
    "be your own boss", "unlimited earning", "passive income",
    "easy money", "quick money", "make money online",
    "data entry", "copy paste job", "form filling job",
    "refer and earn", "mlm", "multi level marketing",
    "network marketing", "business opportunity"
]

LEGITIMATE_SIGNALS = [
    "apply through portal", "official website", "company email",
    "background check", "experience required", "qualification required",
    "interview process", "hr will contact", "offer letter",
    "pf and esi", "health insurance", "annual appraisal"
]

FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "ymail.com", "live.com", "icloud.com",
    "protonmail.com", "tutanota.com"
]

TRUSTED_PLATFORMS = {
    "linkedin.com": 0.9,
    "glassdoor.com": 0.88,
    "indeed.com": 0.82,
    "naukri.com": 0.78,
    "internshala.com": 0.72,
    "shine.com": 0.70,
    "monster.com": 0.75,
    "timesjobs.com": 0.68,
    "unstop.com": 0.70,
    "wellfound.com": 0.80,
}


# ─────────────────────────────────────────
# Core Feature Extraction
# ─────────────────────────────────────────

def extract_all_features(text: str, metadata: dict = None) -> dict:
    """
    Extract all features from cleaned lowercase text + optional metadata.
    Returns a flat dict of feature_name → value.
    """
    if metadata is None:
        metadata = {}

    features = {}

    # ── NLP / Text Features ──
    features["word_count"] = len(text.split())
    features["exclamation_count"] = text.count("!")
    features["caps_ratio"] = metadata.get("caps_ratio", _estimate_caps(text))
    features["urgency_score"] = _count_matches(text, URGENCY_PHRASES)
    features["high_risk_pattern_count"] = _count_matches(text, HIGH_RISK_PATTERNS)
    features["medium_risk_pattern_count"] = _count_matches(text, MEDIUM_RISK_PATTERNS)
    features["legit_signal_count"] = _count_matches(text, LEGITIMATE_SIGNALS)

    # ── Contact Info Features ──
    emails = metadata.get("emails_found", re.findall(
        r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', text
    ))
    features["email_present"] = len(emails) > 0
    features["uses_free_email"] = any(
        _get_email_domain(e) in FREE_EMAIL_DOMAINS for e in emails
    )
    features["uses_company_email"] = (
        len(emails) > 0 and not features["uses_free_email"]
    )
    features["whatsapp_contact"] = bool(
        re.search(r'whatsapp|wa\.me', text, re.I)
    )
    features["telegram_contact"] = bool(
        re.search(r'telegram|t\.me/', text, re.I)
    )

    # ── Red Flag Patterns ──
    features["asks_for_fee"] = bool(re.search(
        r'(registration|training|processing|joining|application)\s*fee|'
        r'pay\s+(to|before)\s+(apply|join|start)|security\s+deposit',
        text, re.I
    ))
    features["asks_for_documents"] = bool(re.search(
        r'(aadhar|aadhaar|pan\s*card|passport|bank\s*account|'
        r'personal\s*documents|identity\s*proof)\s*(required|needed|send|share)',
        text, re.I
    ))
    features["salary_too_high"] = _detect_unrealistic_salary(text)
    features["guaranteed_language"] = bool(re.search(
        r'guaranteed\s+(job|income|salary|placement|selection)',
        text, re.I
    ))
    features["no_experience_claim"] = bool(re.search(
        r'no\s+(experience|qualification|degree)\s+(needed|required|necessary)',
        text, re.I
    ))

    # ── Metadata / Platform Features ──
    features["domain_age_days"] = metadata.get("domain_age_days", 365)
    features["has_ssl"] = int(metadata.get("has_ssl", True))
    features["platform_trust_score"] = _get_platform_score(
        metadata.get("source_platform", "unknown"),
        metadata.get("domain", "")
    )
    features["is_known_platform"] = features["platform_trust_score"] > 0.65

    # ── Structural Features ──
    features["has_company_name"] = _detect_company_name(text)
    features["has_location"] = _detect_location(text)
    features["has_salary_info"] = bool(re.search(
        r'(salary|stipend|ctc|lpa|per\s*month|per\s*annum|₹|\$|inr)',
        text, re.I
    ))
    features["has_job_requirements"] = bool(re.search(
        r'(required|requirement|qualification|skills?\s+needed|'
        r'must\s+have|experience\s+in)',
        text, re.I
    ))
    features["has_company_description"] = bool(re.search(
        r'(about\s+(us|company|organization)|we\s+are\s+a|'
        r'our\s+company|founded\s+in)',
        text, re.I
    ))

    return features


def get_risky_keywords(text: str) -> list:
    """Return list of risky keywords/phrases found in the raw text."""
    text_lower = text.lower()
    found = []

    for phrase in HIGH_RISK_PATTERNS:
        if phrase in text_lower:
            found.append(phrase)

    for phrase in URGENCY_PHRASES:
        if phrase in text_lower and phrase not in found:
            found.append(phrase)

    # Deduplicate and sort by length descending (longer phrases first)
    return sorted(list(set(found)), key=len, reverse=True)[:15]


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def _count_matches(text: str, phrase_list: list) -> int:
    """Count how many phrases from the list appear in text."""
    text_lower = text.lower()
    return sum(1 for phrase in phrase_list if phrase in text_lower)


def _get_email_domain(email: str) -> str:
    """Extract domain from email address."""
    parts = email.lower().split("@")
    return parts[-1] if len(parts) == 2 else ""


def _estimate_caps(text: str) -> float:
    """Estimate capital ratio from lowercase text (fallback)."""
    # After lowercasing, we can't compute this - return 0
    return 0.0


def _detect_unrealistic_salary(text: str) -> bool:
    """Flag salaries that are unrealistically high for entry-level roles."""
    patterns = [
        r'earn\s+\d[\d,]*\s*(per\s+day|daily|\/day)',
        r'(earn|make|get)\s+\d{5,}\s*(per\s+day|daily)',
        r'\d+\s*(lakh|lac)\s*(per\s+week|weekly|per\s+day|daily)',
        r'(50|60|70|80|90|100)\s*k\s*(per\s+day|daily)',
        r'earn\s+(unlimited|lakhs|crore)',
    ]
    return any(re.search(p, text, re.I) for p in patterns)


def _detect_company_name(text: str) -> bool:
    """Check if a company name is mentioned."""
    patterns = [
        r'(pvt\.?\s*ltd|private\s+limited)',
        r'(inc\.|incorporated|llp|llc)',
        r'(company|organization|firm|enterprise)',
        r'(technologies|solutions|services|systems)',
    ]
    return any(re.search(p, text, re.I) for p in patterns)


def _detect_location(text: str) -> bool:
    """Check if a physical location is mentioned."""
    # Common Indian cities + generic location patterns
    cities = [
        "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad",
        "chennai", "pune", "kolkata", "ahmedabad", "jaipur",
        "noida", "gurgaon", "gurugram", "remote", "work from home",
        "onsite", "hybrid", "pan india"
    ]
    text_lower = text.lower()
    return any(city in text_lower for city in cities)


def _get_platform_score(platform: str, domain: str) -> float:
    """Return trust score for the source platform."""
    # Check known platforms by name
    if platform in TRUSTED_PLATFORMS:
        return TRUSTED_PLATFORMS[platform]

    # Check domain string
    for known_domain, score in TRUSTED_PLATFORMS.items():
        if known_domain in domain.lower():
            return score

    return 0.25  # unknown platform = low trust
