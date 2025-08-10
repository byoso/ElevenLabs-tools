
from pathlib import Path

import requests

from . import settings

def debug_text_converter(file_path, title, text):
    # Save txt files simulating a real call to ElevenLabs
    file_path = Path(file_path) / f"debug-{title}.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # file_path = f"{file_path}/debug-{title}.txt"
    with open(file_path, "w") as f:
        f.write(text)


def eleven_labs_converter(char, title, text, file_path):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{char.voice_id}?output_format=mp3_44100_128",
    headers={
        "xi-api-key": f"{settings.ELEVENLABS_API_KEY}"
    },
    json={
        "text": text,
        "model_id": "eleven_multilingual_v2"
    },
    )
    if response.status_code != 200:
        print(f"Something when wrong with {char.name}")

    print(char.name, response.status_code)

    file_path = Path(file_path) / f"{title}.mp3"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Save MP3
    with open(file_path, "wb") as f:
        f.write(response.content)