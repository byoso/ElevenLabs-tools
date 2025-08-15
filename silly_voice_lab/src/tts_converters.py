
from pathlib import Path
import os

import pyttsx3
from pydub import AudioSegment
import requests

from .helpers import Configuration, dprint, SillyVoiceLabError
from .models import Character
from silly_voice_lab.src.silly_engine import c


def process_voice(CONFIG: Configuration, char: Character, title: str, text:str, path:Path) -> None:
    """Converter switch on the appropriate config"""
    match CONFIG.converter:
        case "text":
            debug_text_converter(CONFIG, title, text, path)
        case "prod":
            eleven_labs_converter(CONFIG, char, title, text, path)
        case _: # dev by default
            debug_voice_converter(CONFIG, char, title, text, path)


def debug_voice_converter(CONFIG: Configuration, char: Character, title: str, text: str, path: Path) -> None:
    """Génère un MP3 localement avec pyttsx3."""
    title_wav = title + ".wav"
    title_mp3 = title + ".mp3"
    wav_path = Path(Path(path), Path(title_wav))
    mp3_path = Path(Path(path), Path(title_mp3))
    if os.path.exists(Path(mp3_path)):
        dprint(CONFIG, f"skiped {title_mp3}")
        return
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    if char.gender == "f":
        engine.setProperty('voice', CONFIG.female_voice_id)
    else:
        engine.setProperty('voice', CONFIG.male_voice_id)
    try:
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()
    except Exception as e:
        dprint(CONFIG, f"{c.danger}{e}{c.end}")
    # Conversion WAV → MP3
    try:
        if wav_path:
            sound = AudioSegment.from_wav(wav_path)
            sound.export(mp3_path, format="mp3")
            Path(wav_path).unlink(missing_ok=True)
    except Exception as e:
        raise SillyVoiceLabError(f"{c.danger}Known issue with pydub, voice processing aborted: {char.name}, retry !{c.end}")

    dprint(CONFIG, f"Deleted temporary file: {wav_path}")


def debug_text_converter(CONFIG: Configuration, title: str, text:str, path: Path) -> None:
    """Save txt files simulating a real call to ElevenLabs"""
    file_path = Path(path) / f"{title}.txt"
    if Path(file_path).exists():
        dprint(CONFIG, f"skiped {title}")
        return
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(text)


def eleven_labs_converter(CONFIG: Configuration, char: Character, title: str, text:str, path:Path) -> None:
    file_path = Path(path) / f"{title}.mp3"
    if Path(file_path).exists() or not char.voice_id:
        message = f"skiped {title}"
        if not char.voice_id:
            message += "- NO_VOICE_ID"
        dprint(CONFIG, f"{c.warning}{message}{c.end}")
        return
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{char.voice_id}?output_format=mp3_44100_128",
    headers={
        "xi-api-key": f"{CONFIG.elevenlabs_api_key}"
    },
    json={
        "text": text,
        "model_id": "eleven_multilingual_v2"
    },
    )
    if response.status_code != 200:
        raise SillyVoiceLabError(f"{c.danger}Something when wrong with {char.name}. (still have Eleven Labs credits ?){c.end}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Save MP3
    with open(file_path, "wb") as f:
        f.write(response.content)