"""
Text Preprocessing Utilities
Cleans and normalizes raw job posting text before feature extraction.
"""

import re
import string


def preprocess_text(text: str) -> dict:
    """
    Full preprocessing pipeline for job description text.
    Returns both the cleaned text and extracted raw signals.
    """
    original = text

    # ── Step 1: Basic normalization ──
    text = text.strip()

    # ── Step 2: Count signals BEFORE cleaning (on original) ──
    exclamation_count = original.count('!')
    question_count = original.count('?')
    caps_ratio = (
        sum(1 for c in original if c.isupper()) / max(len(original), 1)
    )

    # ── Step 3: Remove HTML tags ──
    text = re.sub(r'<[^>]+>', ' ', text)

    # ── Step 4: Normalize URLs (replace with token) ──
    text = re.sub(r'http[s]?://\S+|www\.\S+', ' URLTOKEN ', text)

    # ── Step 5: Extract email addresses before removing ──
    emails = re.findall(r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', text)
    text = re.sub(r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', ' EMAILTOKEN ', text)

    # ── Step 6: Extract phone numbers ──
    phones = re.findall(r'\b[\+]?[\d\s\-().]{9,15}\b', text)

    # ── Step 7: Normalize whitespace ──
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # ── Step 8: Lowercase ──
    text_lower = text.lower()

    return {
        "cleaned_text": text_lower,
        "original_text": original,
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "caps_ratio": round(caps_ratio, 4),
        "emails_found": emails,
        "phones_found": phones,
        "word_count": len(text_lower.split()),
        "char_count": len(original),
    }


def normalize_salary_text(text: str) -> str:
    """Normalize various salary formats for comparison."""
    text = text.lower()
    # ₹50,000 → inr 50000
    text = re.sub(r'₹\s*', 'inr ', text)
    text = re.sub(r'\$\s*', 'usd ', text)
    text = re.sub(r',', '', text)
    # 5lpa, 5 lpa, 5l → 500000 annually
    text = re.sub(r'(\d+)\s*lpa?', lambda m: str(int(m.group(1)) * 100000), text)
    return text


def extract_contact_info(text: str) -> dict:
    """Extract all contact details from raw text."""
    emails = re.findall(r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', text, re.I)
    phones = re.findall(r'(\+?[\d][\d\s\-().]{7,14}[\d])', text)
    whatsapp = bool(re.search(r'whatsapp|wa\.me|whatsapp\.com', text, re.I))
    telegram = bool(re.search(r'telegram|t\.me/', text, re.I))

    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "uses_whatsapp": whatsapp,
        "uses_telegram": telegram,
    }
