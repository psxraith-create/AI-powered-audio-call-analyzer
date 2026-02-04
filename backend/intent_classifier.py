"""Hybrid intent/keyword detector.
 - loads scam keywords from data/scam_keywords.txt
 - provides keyword scoring and a tiny TF-IDF + LogisticRegression classifier trained on synthetic samples
"""
from typing import List, Dict, Any
import os

KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scam_keywords.txt')

# Lightweight ML: only used as a small signal; trained on a tiny internal set to demonstrate hybrid approach
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def _load_keywords() -> List[str]:
    if not os.path.exists(KEYWORDS_PATH):
        return ["otp", "account", "blocked", "transfer", "urgent", "kyc", "verify", "bank"]
    with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return lines


SCAM_KEYWORDS = _load_keywords()


def detect_keywords(text: str) -> Dict[str, Any]:
    text_low = text.lower()
    matched = [k for k in SCAM_KEYWORDS if k.lower() in text_low]
    keyword_score = min(100, int(100 * len(matched) / max(1, len(SCAM_KEYWORDS))))
    return {"matched": matched, "keyword_score": keyword_score}


# Tiny synthetic classifier
_classifier = None
_vectorizer = None


def _train_small_model():
    global _classifier, _vectorizer
    if not SKLEARN_AVAILABLE:
        return
    X = [
        "Your account is blocked, share OTP to verify",  # scam
        "Please share your OTP and account number",  # scam
        "We need immediate transfer to lift the hold",  # scam
        "This is a bank alert about your transaction",  # could be scam
        "Hello, I'm calling to confirm your appointment",  # benign
        "Reminder: your electricity bill is due",  # benign
        "Hi, this is a friend calling to check in",  # benign
    ]
    y = [1, 1, 1, 1, 0, 0, 0]
    _vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=2000)
    Xv = _vectorizer.fit_transform(X)
    _classifier = LogisticRegression(max_iter=500)
    _classifier.fit(Xv, y)


if SKLEARN_AVAILABLE:
    _train_small_model()


def classify_intent(text: str) -> Dict[str, Any]:
    """Return probability that the transcript indicates a scam (0..1) and reason tokens."""
    res = detect_keywords(text)
    prob = 0.0
    reason = []
    if SKLEARN_AVAILABLE and _classifier is not None and _vectorizer is not None:
        Xv = _vectorizer.transform([text])
        prob = float(_classifier.predict_proba(Xv)[0][1])
        if prob > 0.5:
            reason.append('ml_high')
    # incorporate keyword presence
    if res['keyword_score'] > 20:
        prob = max(prob, res['keyword_score'] / 100.0)
        reason.append('keywords')

    return {"intent_prob": prob, "reasons": reason, "matched": res['matched'], "keyword_score": res['keyword_score']}
