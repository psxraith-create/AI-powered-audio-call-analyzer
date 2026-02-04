# AI Call Guardian — Hackathon-ready Phone Scam Detection (Judge-focused) ✅

## One-line problem

Phone scams rely on psychological pressure, not consistent phone numbers. Detecting scam _intent and behavior_ in a short call helps stop fraud at the moment of risk.

## Why this matters

- Real-world impact: prevents theft and identity loss from OTP/transfer scams
- Judges care about measurable decisions: we produce transcripts, keywords, behavior signals, and a clear risk rating with human-readable recommendations

---

## System overview (simple flow) 🔧

1. FastAPI receives input via POST /analyze (JSON preferred) or legacy file upload
2. If JSON `text` is provided, it's analyzed immediately (most reliable for demos)
3. Otherwise, optional base64 `audio` or form file is accepted and transcribed (Whisper if available)
4. Intent + keywords + behavioral signals are aggregated into a risk score and short human-readable reasoning

---

## Demo flow (exact steps for the judges) 🎯

1. Start backend: `python -m uvicorn backend.app:app --reload` (server stays on port 8000)
2. Open Swagger UI at `http://127.0.0.1:8000/docs`
3. Use `POST /analyze`:
   - Preferred: choose **application/json** and paste `{ "text": "Your account is blocked, share OTP" }` then Execute
   - Optional: send base64-encoded audio via `audio` field, or use legacy file upload by switching to form-data and uploading `data/sample_scam_call.wav`
4. Inspect returned JSON: `transcript`, `matched_keywords`, `behavior`, `risk` (0–100), `reasoning` (explainers), `severity` (LOW/MEDIUM/HIGH), and `recommended_action`

> Tip: Judges can press `Try it out` on `/analyze` or use the convenience endpoint `/analyze_sample` to run the packaged sample.

---

## Fallback demo mode (feature, not a bug) ⚠️

- To guarantee a smooth hackathon demo, the backend will automatically use a pre-transcribed sample when audio processing/transcription fails or is unavailable.
- Responses include `fallback_mode: true`, `fallback_reason`, and `fallback_note: "Fallback demo mode due to time constraints"` so judges can see the demo mode explicitly.
- This design ensures the demo is rock-solid even without heavyweight audio libs installed.

---

## What we'd add with more time 🚀

- Real-time streaming alerts with sub-second detection
- Enhanced on-device privacy-preserving models and larger multilingual datasets
- Better UIs: judge-facing visualizations (timeline, highlighted risky phrases)
- Post-call automated reporting & secure contact tracing features for support teams

---

## Quick start

1. Install deps: `pip install -r requirements.txt`
2. (Optional) Generate sample audio: `python data/generate_sample_audio.py`
3. Run backend: `python -m uvicorn backend.app:app --reload`
4. Open `http://127.0.0.1:8000/docs` for Swagger UI and demo endpoints

---

## Judgment-ready checklist ✅

- Clear, concise output: transcript + score + short reasoning
- Deterministic demo behavior via fallback mode
- Swagger docs expose the judge-friendly flow

---

If you'd like, I can prepare a short one-slide demo script for the judges and a Streamlit view that highlights `reasoning` + recommended actions.
