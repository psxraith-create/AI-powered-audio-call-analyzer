"""Simple script to test the /analyze endpoint with the sample audio.

Usage:
  python demo/test_analyze.py                    # Uses http://localhost:8000
  python demo/test_analyze.py https://your-codespace-8000.app.github.dev
  BACKEND_URL=http://your-url python demo/test_analyze.py
"""
import requests
from pathlib import Path
import sys
import os

# Get backend URL from environment, argument, or default
backend = os.getenv('BACKEND_URL', 'http://localhost:8000')
if len(sys.argv) > 1:
    backend = sys.argv[1]

SAMPLE = Path(__file__).resolve().parent.parent / 'data' / 'sample_scam_call.wav'

print(f"Backend URL: {backend}")
print(f"Sample audio: {SAMPLE}")

if not SAMPLE.exists():
    print("❌ Sample audio not found. Generate it with:")
    print("   python data/generate_sample_audio.py")
    raise SystemExit(1)

print("\n📤 Uploading and analyzing...")
with open(SAMPLE, 'rb') as f:
    files = {'file': (SAMPLE.name, f, 'audio/wav')}
    try:
        r = requests.post(backend + '/analyze', files=files, timeout=30)
        r.raise_for_status()
        print(f"✓ Status: {r.status_code}")
        print(f"✓ Response:\n")
        import json
        print(json.dumps(r.json(), indent=2))
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {backend}")
        print("   Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

