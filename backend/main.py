"""
FakeJob Detector - FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.feature_extractor import extract_all_features, get_risky_keywords
from utils.preprocessor import preprocess_text
from utils.scraper import scrape_job_url
from utils.scorer import compute_scam_score
from models.classifier import JobScamClassifier

app = FastAPI(
    title="FakeJob Detector API",
    description="Detects whether a job posting is Legitimate, Suspicious, or a Scam",
    version="1.0.0"
)

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML model once at startup
classifier = JobScamClassifier()
classifier.load_or_train()



# Request / Response Models


class TextRequest(BaseModel):
    text: str
    include_highlights: bool = True

class URLRequest(BaseModel):
    url: str

class AnalysisResponse(BaseModel):
    label: str                  # LEGITIMATE / SUSPICIOUS / SCAM
    score: float                # 0–100 scam score
    confidence: float           # 0–1
    reasons: list               # list of red flag strings
    highlighted_keywords: list  # risky words found in text
    ml_probability: float       # raw ML model output
    rule_penalty: float         # points added by rule engine
    feature_breakdown: dict     # individual feature values



# Endpoints


@app.get("/")
def root():
    return {"message": "FakeJob Detector API is running!", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": classifier.is_trained}


@app.post("/analyze/text", response_model=AnalysisResponse)
def analyze_text(request: TextRequest):
    """Analyze a pasted job description text."""
    if len(request.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Text too short. Please paste the full job description."
        )

    # Step 1: Preprocess
    cleaned = preprocess_text(request.text)

    # Step 2: Extract features
    features = extract_all_features(cleaned["cleaned_text"], metadata={})

    # Step 3: ML prediction
    ml_prob = classifier.predict_proba(cleaned["cleaned_text"])

    # Step 4: Hybrid score
    result = compute_scam_score(ml_prob, features)

    # Step 5: Keyword highlights
    keywords = get_risky_keywords(request.text) if request.include_highlights else []

    return AnalysisResponse(
        label=result["label"],
        score=result["score"],
        confidence=result["confidence"],
        reasons=result["reasons"],
        highlighted_keywords=keywords,
        ml_probability=round(ml_prob, 4),
        rule_penalty=result["rule_penalty"],
        feature_breakdown=features
    )


@app.post("/analyze/url", response_model=AnalysisResponse)
def analyze_url(request: URLRequest):
    """Scrape and analyze a job posting URL."""
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Please provide a valid URL starting with http:// or https://")

    # Step 1: Scrape the URL
    scraped = scrape_job_url(request.url)
    if "error" in scraped:
        raise HTTPException(status_code=422, detail=f"Could not scrape URL: {scraped['error']}")

    if len(scraped.get("text", "")) < 50:
        raise HTTPException(status_code=422, detail="Could not extract enough text from the URL.")

    # Step 2: Preprocess
    cleaned = preprocess_text(scraped["text"])

    # Step 3: Extract features (include URL metadata)
    features = extract_all_features(cleaned["cleaned_text"], metadata=scraped)

    # Step 4: ML prediction
    ml_prob = classifier.predict_proba(cleaned["cleaned_text"])

    # Step 5: Hybrid score
    result = compute_scam_score(ml_prob, features)

    # Step 6: Keywords
    keywords = get_risky_keywords(scraped["text"])

    return AnalysisResponse(
        label=result["label"],
        score=result["score"],
        confidence=result["confidence"],
        reasons=result["reasons"],
        highlighted_keywords=keywords,
        ml_probability=round(ml_prob, 4),
        rule_penalty=result["rule_penalty"],
        feature_breakdown=features
    )


@app.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Extract text via OCR and analyze a screenshot of a job posting."""
    try:
        import pytesseract
        from PIL import Image
        import io
        import cv2
        import numpy as np

        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Preprocess for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        pil_img = Image.fromarray(thresh)
        extracted_text = pytesseract.image_to_string(pil_img, config='--psm 6')

        if len(extracted_text.strip()) < 50:
            raise HTTPException(status_code=422, detail="Could not extract enough text from the image.")

        return analyze_text(TextRequest(text=extracted_text))

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="OCR not available. Install pytesseract and Tesseract-OCR to enable image analysis."
        )


@app.post("/train")
def retrain_model():
    """Retrain the model on the latest data."""
    try:
        result = classifier.train()
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
