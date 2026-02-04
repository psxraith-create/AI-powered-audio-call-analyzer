"""Aggregate signals into a final fraud risk score (0..100) and a boolean alert flag."""
from typing import Dict, Any


def compute_risk(intent_prob: float, keyword_score: int, behavior_score: int) -> Dict[str, Any]:
    # Weights tuned for demo clarity (emphasize intent + behavior)
    w_intent = 0.5
    w_keyword = 0.25
    w_behavior = 0.25

    risk = w_intent * (intent_prob * 100) + w_keyword * keyword_score + w_behavior * behavior_score
    risk = min(100.0, max(0.0, risk))
    alert = True if risk >= 55 else False
    return {"risk_score": round(risk, 1), "alert": alert}
