#! /usr/bin/env python3

import os

import requests

from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "no_environment_set")

characters = [
    {"name": "James", "voice_id": "EkK5I93UQWFDigLMpZcX"},
    {"name": "Arabella", "voice_id": "Z3R5wn05IrDiVCyEkUrK"},
    {"name": "Blondie", "voice_id": "exsUS4vynmxd379XN4yO"},
    {"name": "Kuon", "voice_id": "B8gJV1IhpuegLxdpXFOE"},
]


def convert_text_to_speech(char):
    # Create speech (POST /v1/text-to-speech/:voice_id)
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{char['voice_id']}?output_format=mp3_44100_128",
        # f"https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128",
    headers={
        "xi-api-key": f"{ELEVENLABS_API_KEY}"
    },
    json={
        "text": "The first move is what sets everything in motion.",
        "model_id": "eleven_multilingual_v2"
    },
    )
    if response.status_code != 200:
        print(f"Something when wrong with {char['name']}")

    print(char['name'], response.status_code)
    # print(response.json())
        # Sauvegarder le MP3
    file_path = f"{char['name']}.mp3"
    with open(file_path, "wb") as f:
        f.write(response.content)



if __name__ == "__main__":
    for character in characters:
        convert_text_to_speech(character)
    print("Done !")