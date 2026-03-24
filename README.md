# 🛡️ FakeJob Detector

An AI-powered platform that detects whether a job or internship posting is
**Legitimate**, **Suspicious**, or a **Scam** — using Random Forest ML + a rule-based
penalty engine.

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

---

## ✅ Prerequisites

Install these before anything else:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10 or 3.11 | https://python.org/downloads → ✅ check "Add to PATH" |
| Node.js | 18 or 20 LTS | https://nodejs.org |
| VS Code | Latest | https://code.visualstudio.com |

### Recommended VS Code Extensions
Install these from the Extensions panel (Ctrl+Shift+X):
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **ES7+ React/Redux/React-Native snippets**
- **Tailwind CSS IntelliSense**
- **REST Client** (for testing API)

---

## 🚀 Setup & Run (Windows)

### Option A — One-Click Scripts (Easiest)

Open two separate Command Prompt / PowerShell windows:

**Terminal 1 — Backend:**
```
Double-click: scripts\start_backend.bat
```

**Terminal 2 — Frontend:**
```
Double-click: scripts\start_frontend.bat
```

Then open: http://localhost:3000

---

### Option B — Manual Setup (Recommended for learning)

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

---

## 🧪 Running Tests

```bash
# With venv active:
cd backend
venv\Scripts\activate

# Run all tests
pytest ..\tests\ -v

# Or use the script:
..\scripts\run_tests.bat
```

Expected output: **14 tests passing**

---

## 🔌 API Reference

The backend exposes these endpoints:

### POST /analyze/text
```json
// Request
{ "text": "job description here...", "include_highlights": true }

// Response
{
  "label": "SCAM",
  "score": 84.5,
  "confidence": 0.87,
  "reasons": ["Asks you to pay a fee...", "WhatsApp contact only..."],
  "highlighted_keywords": ["registration fee", "whatsapp only"],
  "ml_probability": 0.82,
  "rule_penalty": 21.3,
  "feature_breakdown": { ... }
}
```

### POST /analyze/url
```json
// Request
{ "url": "https://internshala.com/internship/detail/..." }
```

### GET /docs
Interactive Swagger API documentation (built into FastAPI).

---

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

### Rule Penalties (examples)
| Red Flag | Points |
|----------|--------|
| Asks for registration fee | 15 |
| Requests Aadhar/PAN/bank details | 12 |
| Unrealistic salary promise | 10 |
| Guaranteed job/income language | 8 |
| WhatsApp-only contact | 8 |
| Free email (Gmail/Yahoo) | 6 |
| Domain age < 30 days | 7 |
| No company name | 4 |

---

## 📈 Upgrading to a Real Dataset

1. Download: https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction
2. Place `fake_job_postings.csv` in `backend/data/`
3. Edit `backend/models/classifier.py`:

```python
import pandas as pd

def load_kaggle_data():
    df = pd.read_csv("data/fake_job_postings.csv")
    df = df.dropna(subset=["description"])
    # fraudulent column: 1=scam, 0=legit
    df["label"] = df["fraudulent"].map({0: 0, 1: 2})
    return list(zip(df["description"].tolist(), df["label"].tolist()))
```

Then in `load_or_train()`, replace `SAMPLE_TRAINING_DATA` with `load_kaggle_data()`.

---

## 🔧 Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| `python not recognized` | Reinstall Python, check "Add to PATH" |
| `ModuleNotFoundError` | Make sure venv is activated: `venv\Scripts\activate` |
| `CORS error` in browser | Make sure backend is running on port 8000 |
| `npm not found` | Reinstall Node.js from nodejs.org |
| Port 8000 in use | Change port: `uvicorn main:app --port 8001` + update `API_BASE` in App.jsx |
| Model not loading | Delete `backend/models/saved_model.pkl` — it will retrain |

---

## 🚀 Deployment

### Backend → Render (Free)
1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect repo, set:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel (Free)
1. Push to GitHub
2. Go to vercel.com → New Project
3. Set Root Directory: `frontend`
4. Update `API_BASE` in `src/App.jsx` to your Render URL

---

## 📝 Resume Bullet Points

- Built end-to-end fake job detection system using TF-IDF + Random Forest (scikit-learn), extracting 18+ NLP/structural features with a hybrid rule-penalty scoring engine
- Designed FastAPI REST backend with 3 input modalities (text, URL scraping, OCR), returning classification, confidence score, and SHAP-style keyword highlights
- Built React + Tailwind frontend with real-time scam scoring visualization, feature-level explainability panel, and risky keyword highlighting

---

## 📚 Next Steps (Upgrading)

1. **Better model** — fine-tune `bert-base-uncased` on the Kaggle dataset
2. **OCR** — install Tesseract + pytesseract for screenshot input
3. **WHOIS** — `pip install python-whois` for domain age detection
4. **Browser Extension** — see the architecture plan for Chrome extension code
5. **Community reports** — add a `/report` endpoint + SQLite DB
6. **Multilingual** — swap BERT for `xlm-roberta-base`
