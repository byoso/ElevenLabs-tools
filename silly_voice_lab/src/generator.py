from pathlib import Path
import yaml

from silly_voice_lab.src.models import Configuration

from silly_voice_lab.src.helpers import dprint, dpprint, get_groups

CHAR_FILE_DATA = {
            "category": "",
            "dialogues": [
                {"title": "Yes", "text": "Yes !"},
                {"title": "No", "text": "No !"},
            ]
        }


def generate(CONFIG:Configuration, BASE_DIR:str) -> None:
    ROOT_DIR = Path(BASE_DIR, CONFIG.input_folder)
    groups = get_groups(CONFIG)
    for group in groups:
        print(group)
        GROUP_DIR = Path(ROOT_DIR, group.group)
        if GROUP_DIR.exists():
            dprint(CONFIG, f'Path already exists: {GROUP_DIR}')
        else:
            GROUP_DIR.mkdir()
        for char in group.characters:
            CHAR_DIR = Path(GROUP_DIR, char.name)
            if CHAR_DIR.exists():
                dprint(CONFIG, f'Path already exists: {CHAR_DIR}')
            else:
                CHAR_DIR.mkdir()
            data = CHAR_FILE_DATA
            data["category"] = "base_" + char.name
            if Path(CHAR_DIR, f"{char.name}.yaml").exists():
                dprint(CONFIG, f"Skipping: file {char.name}.yaml already exists.")
                continue
            with open(Path(CHAR_DIR, f"{char.name}.yaml"), "w") as f:
                f.write(f"# {char.name} base lines\n\n")
                yaml.dump([data], f, allow_unicode=True, sort_keys=False)
