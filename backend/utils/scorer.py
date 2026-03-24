"""
Hybrid Scam Scoring Engine
Combines ML probability with rule-based penalties.

Formula:
  final_score = (ml_prob × 70) + (rule_penalty × 30/max_penalty)
  
  0–39  → LEGITIMATE
  40–69 → SUSPICIOUS
  70–100 → SCAM
"""


# ─────────────────────────────────────────
# Scoring Rules
# Each rule: (feature_key, threshold, penalty_points, reason_text)
# ─────────────────────────────────────────

PENALTY_RULES = [
    # (feature_key, condition_fn, points, reason)
    ("asks_for_fee",          lambda v: v is True,       15,
     "Asks you to pay a fee to apply or join"),

    ("asks_for_documents",    lambda v: v is True,       12,
     "Requests personal documents (Aadhar/PAN/bank details)"),

    ("salary_too_high",       lambda v: v is True,       10,
     "Promises unrealistically high salary/earnings"),

    ("guaranteed_language",   lambda v: v is True,        8,
     "Uses 'guaranteed job/income' language (classic scam tactic)"),

    ("whatsapp_contact",      lambda v: v is True,        8,
     "Contact is via WhatsApp instead of official email/portal"),

    ("uses_free_email",       lambda v: v is True,        6,
     "Company contact uses a free email (Gmail/Yahoo) instead of corporate domain"),

    ("no_experience_claim",   lambda v: v is True,        6,
     "Claims 'no experience needed' — often used in scam postings"),

    ("high_risk_pattern_count", lambda v: v >= 2,         8,
     "Multiple high-risk phrases detected in the job posting"),

    ("urgency_score",         lambda v: v >= 3,           5,
     "Excessive urgency language used to pressure quick decisions"),

    ("domain_age_days",       lambda v: v < 30,           7,
     "Company website was registered very recently (< 30 days)"),

    ("has_ssl",               lambda v: v == 0,           4,
     "Company website does not have SSL (no HTTPS)"),

    ("platform_trust_score",  lambda v: v < 0.4,          6,
     "Posted on an unknown or low-trust platform"),

    ("caps_ratio",            lambda v: v > 0.20,         3,
     "Excessive use of capital letters — common in spam/scam content"),

    ("telegram_contact",      lambda v: v is True,        5,
     "Contact is via Telegram — unusual for legitimate companies"),

    ("has_company_name",      lambda v: v is False,       4,
     "No company name mentioned in the posting"),

    ("has_location",          lambda v: v is False,       3,
     "No location or remote policy mentioned"),

    ("has_job_requirements",  lambda v: v is False,       3,
     "No job requirements listed — suspicious for a real role"),
]

MAX_POSSIBLE_PENALTY = sum(rule[2] for rule in PENALTY_RULES)

# Bonus deductions for strong legitimate signals
LEGIT_BONUSES = [
    ("legit_signal_count",  lambda v: v >= 3,  -10, "Multiple legitimacy signals present"),
    ("is_known_platform",   lambda v: v is True, -8, "Posted on a trusted job platform"),
    ("uses_company_email",  lambda v: v is True, -5, "Uses a professional corporate email domain"),
    ("has_company_description", lambda v: v is True, -4, "Includes company background/about section"),
]


def compute_scam_score(ml_prob_scam: float, features: dict) -> dict:
    """
    Compute the final hybrid scam score.
    
    Args:
        ml_prob_scam: Probability of being a scam from ML model (0.0–1.0)
        features: Dict of extracted features
    
    Returns:
        Dict with label, score, confidence, reasons, rule_penalty
    """

    # ── Component 1: ML score (0–70) ──
    ml_score = ml_prob_scam * 70

    # ── Component 2: Rule penalties (normalized to 0–30) ──
    raw_penalty = 0
    reasons = []

    for feature_key, condition_fn, points, reason in PENALTY_RULES:
        value = features.get(feature_key)
        if value is not None and condition_fn(value):
            raw_penalty += points
            reasons.append(reason)

    # Apply legit bonuses (can reduce penalty)
    for feature_key, condition_fn, bonus_points, _ in LEGIT_BONUSES:
        value = features.get(feature_key)
        if value is not None and condition_fn(value):
            raw_penalty += bonus_points  # bonus_points are negative

    # Clamp penalty to 0–MAX
    raw_penalty = max(0, min(raw_penalty, MAX_POSSIBLE_PENALTY))

    # Normalize penalty to 0–30 range
    normalized_penalty = (raw_penalty / MAX_POSSIBLE_PENALTY) * 30

    # ── Final Score ──
    final_score = round(ml_score + normalized_penalty, 1)
    final_score = max(0.0, min(100.0, final_score))  # clamp to 0–100

    # ── Classification ──
    if final_score >= 70:
        label = "SCAM"
    elif final_score >= 40:
        label = "SUSPICIOUS"
    else:
        label = "LEGITIMATE"

    # ── Confidence (distance from decision boundaries) ──
    if final_score >= 70:
        confidence = round(min((final_score - 70) / 30 + 0.5, 1.0), 2)
    elif final_score < 40:
        confidence = round(min((40 - final_score) / 40 + 0.4, 1.0), 2)
    else:
        # In the suspicious zone — lower confidence
        dist_from_center = abs(final_score - 55)
        confidence = round(0.3 + (dist_from_center / 30) * 0.4, 2)

    return {
        "label": label,
        "score": final_score,
        "confidence": confidence,
        "reasons": reasons,
        "rule_penalty": round(normalized_penalty, 2),
        "ml_score_component": round(ml_score, 2),
    }


def get_score_color(label: str) -> str:
    """Return a color string for the given label."""
    return {
        "LEGITIMATE": "#16a34a",
        "SUSPICIOUS":  "#d97706",
        "SCAM":        "#dc2626",
    }.get(label, "#6b7280")
