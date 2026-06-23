import edge_tts
import os
from datetime import datetime

VOICES = {
    "female": "en-US-JennyNeural",
    "male": "en-US-GuyNeural",
}
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")


async def text_to_speech(script, voice="female"):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"podcast-{timestamp}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    communicate = edge_tts.Communicate(script, VOICES.get(voice, VOICES["female"]))
    await communicate.save(filepath)

    return filename
