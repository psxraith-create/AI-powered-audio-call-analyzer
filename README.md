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

## Architecture (brief)

- **FastAPI backend** receives audio/requests
- **stt.py**: Transcribes audio (Whisper if available, else simulated)
- **intent_classifier.py**: Detects keywords + intent probability
- **behavior_analyzer.py**: Extracts urgency, repetition, threats, speech speed
- **risk_engine.py**: Aggregates signals into final risk score (0–100) + alert flag

---

## Demo Reliability & Fallback Mode ⚠️

For hackathon reliability, the backend **automatically enables fallback demo mode** when:

- Audio processing unavailable (missing Whisper, ffmpeg, pydub)
- Audio file missing or empty
- STT transcription fails
- No file provided to /analyze

When fallback mode activates:

1. System uses pre-transcribed scam call text from `data/fallback_transcript.txt`
2. Full analysis pipeline runs on fallback text (keywords, intent, behavior, risk)
3. API returns `fallback_mode: true`, `fallback_reason`, and `fallback_message`
4. Server logs: "Fallback demo mode due to time constraints"

This ensures:

- ✅ **All endpoints always return HTTP 200** (never 502/500/timeout)
- ✅ **Judges see realistic analysis** even without audio
- ✅ **Core intelligence is preserved** (keyword + behavior + risk scoring works)
- ✅ **Auto-recovery** if audio deps are installed later

---

## Demo Tips for Judges

1. **Test the Swagger UI** (`/docs`) for interactive endpoint testing
2. **Try /sample or /analyze_sample** for quick demo without uploading audio
3. **Show transcript + matched keywords**: Scammers use predictable patterns (OTP, urgency, impersonation)
4. **Highlight behavior analysis**: Urgency tone + fast speech + repetition = high risk
5. **Emphasize Indian languages**: Hindi/Hinglish support for real-world Indian users
6. **Explain fallback mode**: Why intent-based detection scales better than number-blocking

---

## Project Layout

...
.
├── README.md                          ← You are here
├── requirements.txt                   ← Dependencies
├── backend/
│   ├── app.py                        ← FastAPI main app (0.0.0.0:8000, CORS enabled)
│   ├── stt.py                        ← Speech-to-text wrapper (Whisper + fallback)
│   ├── intent_classifier.py          ← Keyword + ML intent detection
│   ├── behavior_analyzer.py          ← Urgency/threat/repetition analysis
│   ├── risk_engine.py                ← Risk scoring
│   └── __init__.py
├── data/
│   ├── fallback_transcript.txt       ← Pre-transcribed scam example
│   ├── scam_keywords.txt             ← Scam keyword list
│   ├── sample_transcript.txt
│   └── generate_sample_audio.py      ← (Optional) Generate sample audio
├── demo/
│   ├── streamlit_app.py              ← Simple UI for manual testing
│   ├── test_analyze.py
│   └── demo_script.md
└── notebooks/
    └── experiments.ipynb             ← Research & prototyping
```

---

## Networking & Deployment for Codespaces

✅ **FastAPI is configured to bind to 0.0.0.0:8000**

- Accessible via Codespaces port forwarding (automatic public URL)
- No localhost/127.0.0.1 references in code
- CORS enabled for all origins (allow-\*) for hackathon safety
- All endpoints return HTTP 200 with valid JSON

✅ **No external dependencies for core API**

- Optional: Whisper (audio transcription)
- Optional: pydub (audio duration detection)
- Core analysis works without these (falls back to demo mode)

---

## Future Scope

- On-device/edge model for privacy
- Real-time streaming with sub-second alerts
- Additional languages & more robust ML
- Persistent logging for audit trails
- Multi-user session management

---

## Testing

Run TestClient validation (automated on startup):

```bash
python -c "from backend.app import app; from fastapi.testclient import TestClient; client = TestClient(app); print(client.get('/health').json())"
```

---

## License & Attribution

Built for hackathon. Uses Whisper (OpenAI), scikit-learn, and FastAPI.
