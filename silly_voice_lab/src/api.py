#! /usr/bin/env python3

from dataclasses import asdict
from pathlib import Path
import json
import os
import requests
import textwrap

import yaml

from silly_voice_lab.src.helpers import dprint, get_groups, SillyVoiceLabError
from silly_voice_lab.src.models import Character, Configuration, Group
from silly_voice_lab.src.silly_engine import c
from silly_voice_lab.src.tts_converters import process_voice

BASE_DIR = os.getcwd()

# =============================
# ELEVEN LABS CATALOGUE


def _format_data_to_yaml(data: dict, group_name: str="catalogue") -> str:
    characters = []
    for voice in data.get('voices') or []:
        data_gender = "male"
        gender = "m"
        # clean gender
        if voice.get("labels") and voice["labels"].get("gender"):
            data_gender = voice["labels"]["gender"]
        if data_gender == "female":
            gender = "f"
        # clean description
        description = voice.get('description') or ""
        character = Character(
            name=voice.get('name'),
            voice_id=voice.get('voice_id'),
            gender=gender,
            description=description
        )
        characters.append(character)
    from pprint import pprint
    group_obj = Group(
        group="_catalogue",
        characters=characters
    )
    export_group = yaml.dump([asdict(group_obj)], sort_keys=False)
    return export_group

def export_catalogue(CONFIG: Configuration, data: dict) -> None:
    catalogue_file = Path(Path(BASE_DIR), Path(CONFIG.input_folder), Path("_catalogue.yaml"))
    content = _format_data_to_yaml(data)
    with open(catalogue_file, "w") as f:
        f.write(content)
    print(f"{c.success}Catalogue added at {catalogue_file}{c.end}")

def get_catalogue(CONFIG: Configuration, page_size: int =100) -> None:
    response = requests.get(
        url=f"https://api.elevenlabs.io/v2/voices?page_size={page_size}",
        headers={
        "xi-api-key": f"{CONFIG.elevenlabs_api_key}"
    })

    if response.status_code != 200:
        print(f"Something when wrong: {response.text}")
        return

    data = json.loads(response.text)

    print(f"{' Eleven labs available voices ':=^80}")
    total_count = data.get("total_count")
    print(f"Total: {total_count}")
    if data.get("voices"):
        for voice in data["voices"]:
            print(f"{voice['name']:50}{voice['voice_id']}")
            description = voice.get('description') or "---"
            print(textwrap.fill(description, width=80))
            print("-"*80)
        print(f"Total: {len(data['voices'])}")
    else:
        print("No voices in your catalogue :(")

    export_catalogue(CONFIG, data)


# =============================================
# SAMPLES

def create_sample(CONFIG: Configuration) -> None:
    """Create the sample files for all groups in the input_folder"""
    groups = get_groups(CONFIG)
    errors = []
    for group in groups:
        for char in group.characters:
            text_gender = "female" if char.gender == "f" else "male"
            title = f"{char.name}-{char.voice_id}"
            text = f"Hello, my name is {char.name}, my gender is {text_gender}."
            if char.description:
                text += f" I am {char.description}."
            path = Path(Path(BASE_DIR), Path(CONFIG.input_folder), Path(f"_samples-{CONFIG.converter}"), Path(group.group))
            dprint(CONFIG, f"{title}: {text}")
            try:
                process_voice(CONFIG, char, title, text, path)
            except SillyVoiceLabError as e:
                errors.append(char.name)
                print(e)
    if errors:
        print(f"{c.danger}Aborted samples (known pydub error): {len(errors)}{c.end}")
        print(f"{c.danger}{errors}{c.end}")
        print("[dev mode only]: if in dev mode, redo the command a few times until no error remains (do not remove the already created files, just redo the command)")
    else:
        print(f"{c.success}no errors{c.end}")
    print(f"{c.success}Samples done !{c.end}")