"""FastAPI app for AI Call Guardian: /analyze endpoint and a sample endpoint for demo."""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import tempfile

from backend.stt import transcribe
from backend.intent_classifier import classify_intent
from backend.behavior_analyzer import analyze_transcript
from backend.risk_engine import compute_risk

import base64
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title="AI Call Guardian API")

import logging

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
SAMPLE_AUDIO = os.path.abspath(os.path.join(DATA_DIR, 'sample_scam_call.wav'))
FALLBACK_TRANSCRIPT = os.path.abspath(os.path.join(DATA_DIR, 'fallback_transcript.txt'))

# Configure basic logging for demo clarity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def ensure_sample():
    """Try to produce or confirm a sample audio at startup to make the demo robust.
    If audio generation isn't possible (missing deps like gTTS/pydub), ensure that a fallback transcript exists.
    """
    try:
        # attempt to generate sample audio by invoking generator script if sample missing
        if not os.path.exists(SAMPLE_AUDIO) or os.path.getsize(SAMPLE_AUDIO) == 0:
            try:
                import data.generate_sample_audio as gen
                logger.info("Generating sample audio via data.generate_sample_audio")
                gen.main()
            except Exception as e:
                logger.warning(f"Sample audio generation failed: {e}. Falling back to pre-transcribed sample.")

        # Ensure fallback transcript exists
        if not os.path.exists(FALLBACK_TRANSCRIPT):
            logger.info("Creating fallback transcript file")
            with open(FALLBACK_TRANSCRIPT, 'w', encoding='utf-8') as f:
                f.write("Hello, mujhe bank se bol rahe hain, your account is blocked. Please share the OTP you received. It is urgent, transfer kar dijiye otherwise your account will be blocked. This is from bank, verify now.\n")

    except Exception as e:
        logger.exception(f"Unexpected error ensuring sample assets: {e}")


def _generate_reasoning(text: str, intent: dict, behavior: dict, risk: dict) -> List[dict]:
    """Create human-readable reasoning bullets for judges with severity and recommended actions."""
    reasoning = []
    # Keywords-based points
    matched = intent.get('matched', [])
    if matched:
        reasoning.append({
            "reason": f"Matched scam keywords: {', '.join(matched)}",
            "severity": "HIGH" if risk.get('risk_score', 0) >= 70 else "MEDIUM",
            "recommended_action": "Do NOT share OTP or sensitive info. Hang up and contact the institution via official channels."
        })

    # Behavior points
    if behavior.get('urgency_count', 0) > 0:
        reasoning.append({
            "reason": f"Urgency language detected ({behavior.get('urgency_count')} indicators)",
            "severity": "HIGH" if behavior.get('behavior_score', 0) >= 60 else "MEDIUM",
            "recommended_action": "Ask for proof, do not comply with urgent requests. Verify independently."
        })

    if behavior.get('threat_count', 0) > 0:
        reasoning.append({
            "reason": f"Threatening language detected ({behavior.get('threat_count')} indicators)",
            "severity": "HIGH",
            "recommended_action": "Do NOT be intimidated. End the call and verify claims through official channels."
        })

    if behavior.get('words_per_second', 0) > 3.5:
        reasoning.append({
            "reason": "Fast/pressured speech detected",
            "severity": "MEDIUM",
            "recommended_action": "Slow down the conversation and ask questions; do not share codes."
        })

    # ML signal
    if 'ml_high' in intent.get('reasons', []):
        reasoning.append({
            "reason": "Classifier suggests high scam probability",
            "severity": "HIGH",
            "recommended_action": "Treat as suspicious and follow conservative steps (hang up, verify)."
        })

    # Fallback general note if no strong signals
    if not reasoning:
        reasoning.append({
            "reason": "No strong scam indicators detected",
            "severity": "LOW",
            "recommended_action": "If unsure, verify independently before acting."
        })

    return reasoning


def _build_analysis_response(text: str, language: str = 'hi-en', duration: float = 0.0, fallback_mode: bool = False, fallback_reason: str = None, fallback_message: str = None):
    intent = classify_intent(text)
    behavior = analyze_transcript(text, duration)
    risk = compute_risk(intent.get('intent_prob', 0.0), intent.get('keyword_score', 0), behavior.get('behavior_score', 0))

    reasoning = _generate_reasoning(text, intent, behavior, risk)

    # Determine overall severity
    rscore = risk.get('risk_score', 0)
    if rscore >= 70:
        severity = "HIGH"
    elif rscore >= 40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    recommended_action = "Do not share OTPs or sensitive info; hang up and verify via official channels."
    if severity == "LOW":
        recommended_action = "Monitor but verify independently if unsure."
    elif severity == "MEDIUM":
        recommended_action = "Do not share sensitive info; verify caller identity via trusted channels."

    out = {
        "transcript": text,
        "language": language,
        "intent_prob": intent.get('intent_prob'),
        "matched_keywords": intent.get('matched'),
        "keyword_score": intent.get('keyword_score'),
        "behavior": behavior,
        "risk": risk,
        "reasoning": reasoning,
        "severity": severity,
        "recommended_action": recommended_action,
        "fallback_mode": fallback_mode,
        "fallback_reason": fallback_reason,
        "fallback_message": fallback_message,
        "fallback_note": "Fallback demo mode due to time constraints" if fallback_mode else None,
    }
    if fallback_mode:
        logger.info("Fallback demo mode due to time constraints")
    return JSONResponse(content=out)


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    audio: Optional[str] = None  # expect base64-encoded audio bytes (optional)
    simulate: Optional[bool] = False


@app.post("/analyze")
async def analyze(request: Optional[AnalyzeRequest] = None, file: UploadFile = File(None), simulate: bool = Form(False)):
    """Flexible analyze endpoint (JSON preferred):
    - JSON body with `text` (preferred) will be analyzed immediately.
    - Optional `audio` field may contain base64 audio; we attempt STT and fallback cleanly.
    - File upload via form-data (`file`) still supported for backwards compatibility.

    Always returns HTTP 200 and includes `fallback_mode` when demo fallback is used.
    """
    # 1) If JSON text provided, prefer it (most reliable for demos)
    try:
        if request and request.text:
            return _build_analysis_response(request.text, fallback_mode=False)

        # 2) If JSON contains base64 audio, attempt to decode and transcribe
        if request and request.audio:
            try:
                audio_bytes = base64.b64decode(request.audio)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp_path = tmp.name
                    tmp.write(audio_bytes)
                try:
                    stt_res = transcribe(tmp_path, simulate=bool(request.simulate or simulate))
                    text = stt_res.get('text', '')
                    duration = stt_res.get('duration', 0.0)
                    if text and text.strip():
                        return _build_analysis_response(text, language=stt_res.get('language'), duration=duration)
                except Exception as e:
                    logger.warning(f"STT failed on base64 audio: {e}")
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Audio decode failed or invalid base64: {e}")

        # 3) Legacy file upload (form-data)
        if file is not None:
            suffix = os.path.splitext(file.filename)[1] or ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = tmp.name
                shutil.copyfileobj(file.file, tmp)
            try:
                if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                    raise RuntimeError("Uploaded file missing or empty")
                stt_res = transcribe(tmp_path, simulate=simulate)
                text = stt_res.get('text', '')
                duration = stt_res.get('duration', 0.0)
                if text and text.strip():
                    return _build_analysis_response(text, language=stt_res.get('language'), duration=duration)
                raise RuntimeError("Empty transcript returned")
            except Exception as e:
                logger.warning(f"STT failed on uploaded file: {e}")
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        # 4) fallback to pre-transcribed demo transcript
        with open(FALLBACK_TRANSCRIPT, 'r', encoding='utf-8') as f:
            fb_text = f.read()
        return _build_analysis_response(fb_text, fallback_mode=True, fallback_reason="Audio processing unavailable", fallback_message="Fallback demo mode enabled due to time constraints.")

    except Exception as e:
        logger.exception(f"Unexpected error in /analyze handler: {e}")
        # Ensure we always return 200
        with open(FALLBACK_TRANSCRIPT, 'r', encoding='utf-8') as f:
            fb_text = f.read()
        return _build_analysis_response(fb_text, fallback_mode=True, fallback_reason="Internal error", fallback_message="Fallback demo mode enabled due to time constraints.")

@app.get("/sample")
def sample():
    sample_text = (
        "Hello sir, this is the bank security department. "
        "Your account has been flagged for suspicious activity. "
        "Please verify your OTP immediately or your account will be blocked."
    )
    # Use same analysis pipeline so sample mirrors /analyze output structure
    return _build_analysis_response(sample_text, fallback_mode=True, fallback_reason="Demo sample", fallback_message="Fallback demo mode enabled due to time constraints.")

@app.get('/analyze_sample')
def analyze_sample():
    """One-click analysis endpoint for judges: analyzes the server-side sample audio or fallback transcript.
    This endpoint exists so Swagger users can press Execute without uploading files.
    """
    try:
        if os.path.exists(SAMPLE_AUDIO) and os.path.getsize(SAMPLE_AUDIO) > 0:
            try:
                stt_res = transcribe(SAMPLE_AUDIO, simulate=False)
                text = stt_res.get('text', '')
                duration = stt_res.get('duration', 0.0)
                if not text or not text.strip():
                    raise RuntimeError('Empty transcript from sample')
                return _build_analysis_response(text, language=stt_res.get('language'), duration=duration)
            except Exception as e:
                logger.warning(f"Sample STT failed: {e}")
        # fallback
        with open(FALLBACK_TRANSCRIPT, 'r', encoding='utf-8') as f:
            fb_text = f.read()
    except Exception as e:
        logger.exception(f"Error in analyze_sample: {e}")
        fb_text = "Hello, mujhe bank se bol rahe hain, your account is blocked. Please share the OTP you received. It is urgent, transfer kar dijiye otherwise your account will be blocked. This is from bank, verify now."
    return _build_analysis_response(fb_text, fallback_mode=True, fallback_reason="Audio processing unavailable", fallback_message="Fallback demo mode enabled due to time constraints.")
