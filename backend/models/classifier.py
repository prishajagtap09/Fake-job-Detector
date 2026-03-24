"""
Job Scam Classifier
Uses TF-IDF + Random Forest ensemble.
Trains on a small built-in dataset if no saved model is found.
In production, replace with BERT or train on the Kaggle dataset.
"""

import os
import pickle
import json
from pathlib import Path


MODEL_PATH = Path(__file__).parent / "saved_model.pkl"
VECTORIZER_PATH = Path(__file__).parent / "saved_vectorizer.pkl"




SAMPLE_TRAINING_DATA = [
    # (text, label)  label: 0=legit, 1=suspicious, 2=scam
    
    # ── LEGITIMATE SAMPLES ──
    ("We are a mid-sized IT company looking for a Python developer with 2+ years of experience. "
     "The role involves building REST APIs using FastAPI and PostgreSQL. "
     "Salary: 8-12 LPA. Apply through our official portal. Interview process includes "
     "a technical round and HR discussion. Company email: hr@techcorp.com", 0),

    ("XYZ Solutions Pvt Ltd is hiring a Marketing Intern for 3 months. "
     "Stipend: ₹15,000/month. Required skills: content writing, social media management. "
     "Location: Bangalore (hybrid). Final year students can apply. "
     "Send CV to internships@xyzsolutions.com", 0),

    ("Looking for a Data Analyst with strong SQL and Excel skills. "
     "2-4 years experience required. CTC: 6-9 LPA. "
     "About us: We are a fintech startup founded in 2018, backed by Sequoia. "
     "Background verification will be conducted. PF and health insurance provided.", 0),

    ("Senior Software Engineer - Java Backend. 5+ years experience. "
     "Skills: Spring Boot, Microservices, AWS. CTC: 18-25 LPA. "
     "Location: Hyderabad (onsite). Company: ABC Technologies Ltd. "
     "Apply via Naukri or email resume to careers@abctech.com. "
     "Shortlisted candidates will be contacted for a video interview.", 0),

    ("Research Internship at IIT Delhi. Duration: 2 months summer internship. "
     "Stipend: ₹20,000/month. Domain: Machine Learning and NLP. "
     "Qualification: B.Tech/M.Tech in CS or related field. "
     "No application fee. Contact: research@iitd.ac.in", 0),

    ("Product Manager role at a Series B startup. 3-6 years experience. "
     "You will own the product roadmap, work with engineering and design teams. "
     "Salary: 20-30 LPA + ESOPs. Good communication and analytical skills required. "
     "Apply through our careers page. We are an equal opportunity employer.", 0),

    # ── SUSPICIOUS SAMPLES ──
    ("Exciting work from home opportunity! Flexible hours, earn 25000-50000 per month. "
     "Data entry and form filling work. No experience needed. "
     "Training provided. Contact us on WhatsApp for details. "
     "Limited slots available. Apply immediately.", 1),

    ("Hiring for multiple positions! Earn good salary from home. "
     "Part time and full time available. Be your own boss. "
     "Unlimited earning potential. Contact on telegram for more info. "
     "Send your details to hr.jobs2024@gmail.com", 1),

    ("We need freelancers for online tasks. Earn 500-1000 per day easily. "
     "Work just 2-3 hours. No investment required. "
     "Refer and earn bonus. Work from anywhere. "
     "Message us NOW on WhatsApp: +91 99XXXXXXXX. Don't miss this chance!", 1),

    ("Digital marketing executive wanted urgently. Freshers welcome. "
     "Salary: upto 40000/month. No experience required. "
     "Immediate joining. Interview today only. "
     "Call or WhatsApp on the number given. This opportunity will not last.", 1),

    ("Business development associate. Network marketing company. "
     "Build your own team and earn passive income. "
     "Training provided at our office. Small investment required to start. "
     "100% support and guidance. Earn unlimited. Contact: bizops@gmail.com", 1),

    # ── SCAM SAMPLES ──
    ("URGENT HIRING! Earn 50,000 per day from home! "
     "No experience needed. No qualification required. "
     "Registration fee: ₹500 only (fully refundable). "
     "Send Aadhar card and bank account details to join. "
     "WhatsApp ONLY: +91 98XXXXXXXX. HURRY! Only 10 seats left!", 2),

    ("Get guaranteed job in MNC! 100% placement guaranteed. "
     "Just pay ₹2000 registration fee and we will arrange interview. "
     "Send your documents and PAN card to apply. "
     "No interview required. Direct joining offer letter in 2 days. "
     "Contact on WhatsApp only. Do NOT miss this golden opportunity!", 2),

    ("Work from home and earn 1 lakh per month! Guaranteed income! "
     "Simple copy paste tasks. Earn daily. "
     "Pay joining fee ₹999 and start earning same day. "
     "100% genuine. Aadhar required for verification. "
     "Limited time offer! Apply IMMEDIATELY on WhatsApp.", 2),

    ("Dear candidate, you have been selected for a job in Dubai! "
     "Salary: 3000 USD per month. No experience needed. "
     "You only need to pay ₹5000 for visa processing and air ticket. "
     "Send your passport copy and bank details for further processing. "
     "Hurry! Seats are filling up. This is 100% genuine offer.", 2),

    ("Earn ₹50,000 to ₹1,00,000 weekly from home! "
     "Online trading job. We will train you. "
     "Investment of just ₹2000 to start. Get returns in 24 hours. "
     "WhatsApp us now for registration. Limited seats! "
     "Pay registration fee today and secure your spot. Guaranteed profit!", 2),

    ("JOB ALERT!!! URGENT REQUIREMENT!!! "
     "Salary: 80,000 PER DAY!!! Work just 1 hour! "
     "No degree needed! No experience needed! Just send your AADHAR CARD "
     "and pay ₹1,500 security deposit. Get offer letter same day! "
     "WHATSAPP ONLY: Hurry up this offer expires TONIGHT!!!!", 2),
]


class JobScamClassifier:
    """
    TF-IDF + Random Forest classifier for job scam detection.
    """

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_trained = False

    def load_or_train(self):
        """Load saved model or train a new one."""
        if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
            try:
                self._load()
                print("✓ Model loaded from disk.")
                return
            except Exception as e:
                print(f"⚠ Could not load model: {e}. Retraining...")

        print("⚙ Training model on sample data...")
        self.train()

    def train(self, custom_data=None) -> str:
        """Train the classifier."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.pipeline import Pipeline

            data = custom_data or SAMPLE_TRAINING_DATA
            texts = [d[0] for d in data]
            labels = [d[1] for d in data]

            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
            )
            X = self.vectorizer.fit_transform(texts)

            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                class_weight="balanced",
                random_state=42,
            )
            self.model.fit(X, labels)
            self.is_trained = True

            # Save to disk
            self._save()

            msg = f"Model trained on {len(texts)} samples. Classes: {set(labels)}"
            print(f"✓ {msg}")
            return msg

        except ImportError:
            print("⚠ scikit-learn not installed. Using rule-based fallback.")
            self.is_trained = False
            return "scikit-learn not available — using rule-based scoring only"

    def predict_proba(self, text: str) -> float:
        """
        Return probability of being a SCAM (class 2).
        Falls back to 0.5 if model is not available.
        """
        if not self.is_trained or self.model is None:
            return 0.5  # neutral — rely on rule engine

        try:
            X = self.vectorizer.transform([text])
            proba = self.model.predict_proba(X)[0]

            # Classes: [0=legit, 1=suspicious, 2=scam]
            classes = list(self.model.classes_)

            scam_prob = 0.0
            suspicious_prob = 0.0

            if 2 in classes:
                scam_prob = proba[classes.index(2)]
            if 1 in classes:
                suspicious_prob = proba[classes.index(1)]

            # Combined scam-leaning probability
            return round(scam_prob + (suspicious_prob * 0.4), 4)

        except Exception as e:
            print(f"Prediction error: {e}")
            return 0.5

    def _save(self):
        """Persist model to disk."""
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def _load(self):
        """Load model from disk."""
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)
        self.is_trained = True
