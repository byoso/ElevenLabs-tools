
import os

from dotenv import load_dotenv

load_dotenv()

# user params
INPUT_FOLDER = os.environ.get("INPUT_FOLDER", "scenario")
OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", "voices")


# developpers
DEBUG = os.environ.get("DEBUG", "1") == "1"
CONVERTER = os.environ.get("CONVERTER", "text")

# Secrets
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "no_environment_set")
