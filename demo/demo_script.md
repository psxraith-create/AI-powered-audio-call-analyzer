# Demo Script — AI Call Guardian

## Starting the Backend

For local development (or GitHub Codespaces):

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- **Local**: `http://localhost:8000`
- **Codespaces**: `https://<codespace-name>-8000.app.github.dev`

## Demo Methods

### Method 1: Swagger UI (Recommended for judges)

Open the interactive API docs in your browser:

- **Local**: `http://localhost:8000/docs`
- **Codespaces**: `https://<codespace-name>-8000.app.github.dev/docs`

Then press "Execute" on any endpoint without uploading files (uses fallback demo).

### Method 2: One-Click Sample Analysis

Get instant scam analysis without uploading:

```bash
# Local
curl http://localhost:8000/analyze_sample

# Codespaces
curl https://<codespace-name>-8000.app.github.dev/analyze_sample
```

### Method 3: Sample Audio Upload

Upload audio file to analyze:

```bash
# Local (with file)
curl -X POST -F "file=@data/sample_scam_call.wav" http://localhost:8000/analyze

# Local (empty - triggers fallback demo)
curl -X POST http://localhost:8000/analyze

# Codespaces
curl -X POST https://<codespace-name>-8000.app.github.dev/analyze
```

### Method 4: Streamlit Demo UI

For interactive demo with upload interface:

```bash
streamlit run demo/streamlit_app.py
```

Then enter your backend URL in the sidebar (e.g., `http://localhost:8000` or the Codespaces public URL).

## (Optional) Generate Sample Audio

```bash
python data/generate_sample_audio.py
```

_Note: Requires gTTS and ffmpeg. If unavailable, the system uses pre-transcribed text._

## What the Demo Shows

✅ **Live Transcript** — Speech recognized from audio (or fallback demo text)
✅ **Matched Keywords** — Scam indicators: OTP, account, blocked, urgent, transfer, etc.
✅ **Behavioral Analysis** — Urgency tone, speech speed, repetition patterns
✅ **Risk Score (0–100)** — Final fraud probability with alert threshold (>55 = high risk)
✅ **Fallback Mode** — Automatic graceful degradation if audio processing unavailable

## Presentation Talking Points

1. **Why Intent-Based?**
   - Number-blocking fails because scammers rotate numbers
   - Our AI detects the _psychology_ of scams: urgency, impersonation, threats
2. **Multilingual Support**
   - English, Hindi, Hinglish (mixed language calls)
   - Critical for Indian market where code-switching is common
3. **Hybrid Approach**
   - Rule-based keyword matching (fast, interpretable)
   - Behavioral heuristics (urgency, fast speech, repetition)
   - Lightweight ML classifier (scalable, lightweight)
4. **Reliability in Live Demo**
   - Automatic fallback demo mode
   - All endpoints always return HTTP 200
   - No crashes, timeouts, or 500 errors even if audio unavailable

## Demo Troubleshooting

| Issue                       | Solution                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------- |
| Codespaces URL doesn't load | Check port 8000 is exposed: bottom panel → "Ports" → ensure visibility is "Public" |
| Audio processing slow       | Use `/sample` or `/analyze_sample` endpoints (no audio processing)                 |
| ffmpeg warnings             | Normal in Codespaces; system auto-switches to fallback demo mode                   |
| Whisper not available       | System falls back to simulated transcription automatically                         |

---

**🎯 Bottom Line**: Judges see real AI analysis with zero friction, even without audio dependencies.
