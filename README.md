## One-line problem

Phone scams succeed by pressuring people — not by using the same phone numbers. Detecting scam intent and risky behavior inside a short call can stop fraud the moment someone is most at risk.

## Why this matters

- Real-world impact: helps prevent theft and identity loss from OTP and transfer scams.
- Judges and evaluators want measurable outputs: we return a transcript, detected keywords, behavioral signals, a clear risk score, and short human-readable recommendations.

---

## System overview (simple flow) 🔧

1. FastAPI accepts input through POST /analyze (JSON is preferred) or the legacy file upload route.
2. If the JSON request includes `text`, we analyze it immediately (this is the most reliable demo path).
3. Otherwise, you can provide base64 `audio` or upload a file; the server will transcribe it (Whisper if available).
4. We combine intent, matched keywords, and behavioral signals into a risk score and a concise, human-readable explanation.

---

## Demo flow (exact steps for judges) 🎯

1. Start the backend:

   python -m uvicorn backend.app:app --reload

   The server defaults to port 8000.

2. Open the Swagger UI at http://127.0.0.1:8000/docs
3. Use POST /analyze:
   - Preferred: choose `application/json` and send a payload like:

     { "text": "Your account is blocked, share OTP" }

     then click Execute.
   - Optional: send base64-encoded audio via the `audio` field, or switch to form-data and upload `data/sample_scam_call.wav`.
4. Inspect the returned JSON: `transcript`, `matched_keywords`, `behavior`, `risk` (0–100), `reasoning` (short explainers), `severity` (LOW/MEDIUM/HIGH), and `recommended_action`.

Tip: Judges can also press "Try it out" on `/analyze` or use the convenience endpoint `/analyze_sample` to run the included example.

---

## Fallback demo mode (intentional for reliability) ⚠️

To make demos rock-solid, the backend automatically falls back to a pre-transcribed sample when audio transcription fails or heavy audio libraries are not available.

Responses indicate this explicitly with `fallback_mode: true`, plus `fallback_reason` and `fallback_note: "Fallback demo mode due to time constraints"`. This keeps the demo deterministic and judge-friendly.

---

## What we'd build with more time 🚀

- Real-time streaming alerts with sub-second detection.
- Stronger privacy and on-device models with larger multilingual datasets.
- Judge-facing UIs: timelines, highlighted risky phrases, and interactive visualizations.
- Post-call automated reporting and secure contact-tracing tools for support teams.

---

## Quick start

1. Install dependencies:

   pip install -r requirements.txt

2. (Optional) Generate the sample audio:

   python data/generate_sample_audio.py

3. Run the backend:

   python -m uvicorn backend.app:app --reload

4. Open http://127.0.0.1:8000/docs to access Swagger UI and demo endpoints.

---

## Judgment-ready checklist ✅

- Clear, concise outputs: transcript, risk score, and a short explanation.
- Deterministic demo behavior via fallback mode.
- Swagger docs expose a judge-friendly flow.

---

If you'd like, I can also:

- Draft a one-slide demo script for judges.
- Build a simple Streamlit view that highlights `reasoning` and `recommended_action` for quick manual review.

Say which you'd prefer and I’ll add it next.