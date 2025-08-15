#! /usr/bin/env python3


import os
import sys
from pathlib import Path

import pyttsx3
import yaml
import shutil


from silly_voice_lab.src.generator import generate
from silly_voice_lab.src.api import create_sample, get_catalogue
from silly_voice_lab.src.helpers import dprint, dpprint, get_config, get_groups, SillyVoiceLabError
from silly_voice_lab.src.models import Character, Configuration, Group
from silly_voice_lab.src.silly_engine import print_title, c
from silly_voice_lab.src.tts_converters import process_voice

VERSION = "0.2.5"
BASE_DIR = os.getcwd()
INIT_PROJECT_INIT = "/src/init_project/init/"
INIT_PROJECT_EXPERT = "/src/init_project/expert/"


def get_scripts(CONFIG: Configuration, group: Group) -> None:
    errors = []
    group_folder_path = Path(Path(BASE_DIR), Path(CONFIG.input_folder), Path(group.group))
    dprint(CONFIG, group_folder_path)
    for char in group.characters :
        folder_path = Path(group_folder_path, Path(char.name))
        for file in folder_path.glob("*.yaml"):
            dprint(CONFIG, f"\nReading {file.name} ...")

            with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
                scene_text = yaml.safe_load(f)
                for scene in scene_text:
                    category = scene['category']
                    dprint(CONFIG, f"\n{char.name} is recording the dialogues for {category} scenes:")
                    voice_folder_path = Path(Path(BASE_DIR), Path(CONFIG.output_folder), Path(group.group), Path(char.name), Path(category))
                    for dialogue in scene['dialogues']:
                        dprint(CONFIG, f"- {dialogue['title']}")
                        try:
                            process_voice(CONFIG, char, dialogue['title'], dialogue['text'], voice_folder_path)
                        except SillyVoiceLabError as e:
                            errors.append(char.name)
                            print(e)
    if errors:
        message = f"{c.danger}Errors: {len(errors)}\n{errors}{c.end}"
        raise SillyVoiceLabError(message)



def start_process(file_name: str="dialogues.cfg") -> None:
    CONFIG = get_config(file_name)
    groups = get_groups(CONFIG)
    errors = 0
    for group in groups:
        try:
            get_scripts(CONFIG, group)
        except SillyVoiceLabError as e:
            errors += 1
            print(e)
    if errors > 0:
        raise SillyVoiceLabError(f"{c.danger}Errors occured, read the logs to know more.{c.end}")

def pyttsx_infos() -> None:
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    print(f"|{'Language':^45} | {'Code':^30}|")
    print("|" + "-" * 79 + "|")
    for voice in voices:
        print(f"|{voice.name:45} | {str(voice.languages):30}|")
        print("|" + "-" * 78 + "|")

def get_init_files(project_folder: str="/src/init_project/init/") -> None:
    this_location = os.path.dirname(os.path.abspath(__file__))
    src_folder = this_location + project_folder
    dest_folder = BASE_DIR
    for item in os.listdir(src_folder):
        s = os.path.join(src_folder, item)
        d = os.path.join(dest_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def cmd() -> None:
    # CLI interface
    if len(sys.argv) == 2:
        if sys.argv[1] == "cat":
            pyttsx_infos()
        if sys.argv[1] == "init":
            get_init_files(INIT_PROJECT_INIT)
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        file_name = sys.argv[2]
        try:
            start_process(file_name)
        except SillyVoiceLabError as e:
            print(e)
        print(f"{c.success}Done !{c.end}")
    elif len(sys.argv) == 3 and sys.argv[1] == "gen":
        file_name = sys.argv[2]
        CONFIG = get_config(file_name)
        generate(CONFIG, BASE_DIR)
    elif len(sys.argv) == 3 and sys.argv[1] == "cat":
        file_name = sys.argv[2]
        CONFIG = get_config(file_name)
        get_catalogue(CONFIG)
    elif len(sys.argv) == 3 and sys.argv[1] == "sample":
        file_name = sys.argv[2]
        CONFIG = get_config(file_name)
        create_sample(CONFIG)
    elif len(sys.argv) == 3 and sys.argv[1] == 'init' and sys.argv[2] == "expert":
        get_init_files(INIT_PROJECT_EXPERT)

    else:
        print_title("Silly Voice lab", step=2)
        title_bar = f" Silly Voice Lab v{VERSION} - A tool for ElevenLab voice creation "
        print(f"\n{title_bar:=^80}\n")
        print(f"{'Action':^35}|{'Command'}")
        print("_"*80)
        readme = (
            ("* PROJECT INITIALIZATION", ''),
            ("Get a basic starter pack", 'silly-voice-lab init'),
            ("Get an expert starter pack (linux)", "silly-voice-lab init expert"),
            ("* LIST VOICES AVAILABLE",""),
            ("For dev mode", "silly-voice-lab cat"),
            ("Catalogue group file (Elevenlabs)", "silly-voice-lab cat <your_conf.cfg>"),
            ("* PROCESSING",""),
            ("Get sample files (in input_folder)", "sill_voice_lab sample <your_conf.cfg>"),
            ("Generate the characters files", "silly-voice-lab gen <your_conf.cfg>"),
            ("Run the voicing based on your cfg", "silly-voice-lab run <your_conf.cfg>"),
        )
        for desc, cmd in readme:
            if desc.startswith("*"):
                print(f"\n{desc}")
            else:
                print(f"{desc:35}|{cmd:40}")

        print(
            "\nA usefull 'readme' and the source code here:\n",
            "https://github.com/byoso/ElevenLabs-tools\n",
        )

if __name__ == "__main__":
    cmd()