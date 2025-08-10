#! /usr/bin/env python3

import os
from pathlib import Path
from pprint import pprint

import yaml

from src import settings
from src.models import Character, Group
from src.tts_converters import debug_text_converter, eleven_labs_converter


BASE_DIR = os.getcwd()
converter = settings.CONVERTER


class TtsConverterError(Exception):
    pass


def dprint(*args, **kwargs):
    if settings.DEBUG:
        print(*args, **kwargs)

def dpprint(*args, **kwargs):
    if settings.DEBUG:
        pprint(*args, **kwargs)

def get_groups() -> list[Group]:
    groups = []
    folder_path = Path(Path(BASE_DIR), Path(settings.INPUT_FOLDER))
    for file in folder_path.glob("*.yaml"):
        dprint(f"\nReading {file.name} ...")

        with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
            casting = yaml.safe_load(f)
            for group in casting:
                grp = Group(**group)
                grp.characters = [Character(**char) for char in grp.characters]
                groups.append(grp)
    return groups


def convert_text_to_speech(char, title, text, file_path):
    # Create speech (POST /v1/text-to-speech/:voice_id)
    match settings.CONVERTER:
        case "text":
            debug_text_converter(file_path, title, text)
        case "prod":
            eleven_labs_converter(char, title, text, file_path)
        case "dev":
            print("not implemented yet")


def get_scripts(group: Group):
    group_folder_path = Path(Path(BASE_DIR), Path(settings.INPUT_FOLDER), Path(group.folder))
    dprint(group_folder_path)
    for char in group.characters :
        dprint(f"\n# {char.name} is working on the scenario...")
        folder_path = Path(group_folder_path, Path(char.name))
        for file in folder_path.glob("*.yaml"):
            dprint(f"\nReading {file.name} ...")

            with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
                scene_text = yaml.safe_load(f)
                for scene in scene_text:
                    category = scene['category']
                    dprint(f"\n{char.name} is recording the dialogues for {category} scenes:")
                    voice_folder_path = Path(Path(BASE_DIR), Path(settings.OUTPUT_FOLDER+f"-{converter}"), Path(group.name), Path(char.name), Path(category))
                    for dialogue in scene['dialogues']:
                        dprint(f"- {dialogue['title']}")
                        convert_text_to_speech(char, dialogue['title'], dialogue['text'], voice_folder_path)



def main():
    groups = get_groups()
    for group in groups:
        dpprint(group)
        get_scripts(group)

    print("Done !")



if __name__ == "__main__":
    main()