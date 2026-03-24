# 🛡️ FakeJob Detector

An AI-powered platform that detects whether a job or internship posting is
**Legitimate**, **Suspicious**, or a **Scam** — using Random Forest ML + a rule-based
penalty engine.

- Built end-to-end fake job detection system using TF-IDF + Random Forest (scikit-learn), extracting 18+ NLP/structural features with a hybrid rule-penalty scoring engine
- Designed FastAPI REST backend with 3 input modalities (text, URL scraping, OCR), returning classification, confidence score, and SHAP-style keyword highlights
- Built React + Tailwind frontend with real-time scam scoring visualization, feature-level explainability panel, and risky keyword highlighting

---

## 📁 Project Structure

```
fakejob-detector/
├── backend/                   ← Python FastAPI server
│   ├── main.py                ← API entry point & all endpoints
│   ├── requirements.txt       ← Python dependencies
│   ├── utils/
│   │   ├── preprocessor.py    ← Text cleaning & normalization
│   │   ├── feature_extractor.py ← 18+ signal extraction
│   │   ├── scorer.py          ← Hybrid ML + rule scoring engine
│   │   └── scraper.py         ← URL scraping (BeautifulSoup)
│   └── models/
│       └── classifier.py      ← TF-IDF + Random Forest ML model
│
├── frontend/                  ← React + Vite + Tailwind UI
│   ├── src/
│   │   ├── App.jsx            ← Root component & API calls
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── InputPanel.jsx     ← Text/URL input with examples
│   │       ├── AnalysisResult.jsx ← Score, label, breakdown
│   │       ├── HighlightedText.jsx ← XAI keyword highlighting
│   │       ├── FeatureBreakdown.jsx ← Feature-by-feature display
│   │       └── HowItWorks.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── tests/
│   └── test_backend.py        ← pytest unit + integration tests
│
└── scripts/
    ├── start_backend.bat      ← One-click Windows backend start
    ├── start_frontend.bat     ← One-click Windows frontend start
    └── run_tests.bat          ← Run all tests
```

--
---

###  — Manual Setup 

#### Step 1: Open project in VS Code
```
File → Open Folder → select fakejob-detector
```

#### Step 2: Backend Setup
Open Terminal in VS Code (Ctrl + `) and run:

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# You should see (venv) in your terminal prompt

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

You should see:
```
✓ Model trained on 17 samples.
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Step 3: Frontend Setup
Open a **second terminal** (click + in VS Code terminal panel):

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start React dev server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in 300ms
  ➜  Local:   http://localhost:3000/
```

#### Step 4: Open the app
Visit: **http://localhost:3000**




## 🧠 How the Scoring Works

```
Final Score (0–100) = ML Score (0–70) + Rule Penalty (0–30)

ML Score     = RandomForest probability × 70
Rule Penalty = Sum of triggered rule points, normalized to 30

Thresholds:
  0–39  → LEGITIMATE  ✅
  40–69 → SUSPICIOUS  ⚠️
  70+   → SCAM        ❌
```





- Built end-to-end fake job detection system using TF-IDF + Random Forest (scikit-learn), extracting 18+ NLP/structural features with a hybrid rule-penalty scoring engine
- Designed FastAPI REST backend with 3 input modalities (text, URL scraping, OCR), returning classification, confidence score, and SHAP-style keyword highlights
- Built React + Tailwind frontend with real-time scam scoring visualization, feature-level explainability panel, and risky keyword highlighting

---

