"""Behavior analysis: urgency, repetition, fast-speech and threat detection.
Returns a behavior score (0..100) and supportive metrics.
"""
from typing import Dict, Any
import re

URGENCY_WORDS = set(["urgent", "immediately", "now", "asap", "jaldi", "turant", "abhi", "urgent action", "transfer kar", "block"])
THREAT_WORDS = set(["police", "case", "arrest", "fine", "legal action", "kotwal"])


def _count_repetition(text: str) -> float:
    words = re.findall(r"\w+", text.lower())
    if not words:
        return 0.0
    from collections import Counter
    c = Counter(words)
    repeats = sum(v - 1 for v in c.values() if v > 1)
    return repeats / len(words)


def analyze_transcript(text: str, duration: float) -> Dict[str, Any]:
    words = re.findall(r"\w+", text)
    word_count = len(words)
    wps = (word_count / duration) if duration and duration > 0 else 0.0

    urgency_count = sum(1 for w in URGENCY_WORDS if w in text.lower())
    threat_count = sum(1 for w in THREAT_WORDS if w in text.lower())
    repetition_ratio = _count_repetition(text)

    # behavior score composition (weights chosen for demonstrative effect)
    score = 0.0
    # fast speech (wps > 3.5 is unusual fast for phone calls)
    if wps > 3.5:
        score += 30
    # urgency words
    score += min(30, urgency_count * 10)
    # repetition
    score += min(20, repetition_ratio * 100)
    # threats
    score += min(20, threat_count * 10)

    score = min(100, int(score))

    return {
        "word_count": word_count,
        "duration": duration,
        "words_per_second": round(wps, 2),
        "urgency_count": urgency_count,
        "threat_count": threat_count,
        "repetition_ratio": round(repetition_ratio, 3),
        "behavior_score": score,
    }
