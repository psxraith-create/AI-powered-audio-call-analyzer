"""Generate a sample scam audio (English/Hinglish) using gTTS (if available).
Creates: data/sample_scam_call.wav
"""
import os
from pathlib import Path

TEXT = (
    "Hello, mujhe bank se bol rahe hain. Your account is blocked. "
    "Please share the OTP you received. It is urgent — transfer kar dijiye otherwise your account will be blocked. "
    "This is from bank, verify now."
)

OUT = Path(__file__).resolve().parent / 'sample_scam_call.wav'


def main():
    try:
        from gtts import gTTS
        from pydub import AudioSegment
    except Exception as e:
        print("gTTS or pydub not installed. Install with: pip install gTTS pydub")
        print("Or manually provide data/sample_scam_call.wav")
        return

    tts = gTTS(TEXT, lang='hi')
    tmp_mp3 = Path('tmp_demo.mp3')
    print('Generating TTS mp3...')
    tts.save(str(tmp_mp3))

    print('Converting mp3 -> wav (mono, 16k)...')
    aud = AudioSegment.from_mp3(str(tmp_mp3)).set_frame_rate(16000).set_channels(1)
    aud.export(str(OUT), format='wav')
    tmp_mp3.unlink()
    print('Generated:', OUT)


if __name__ == '__main__':
    main()
