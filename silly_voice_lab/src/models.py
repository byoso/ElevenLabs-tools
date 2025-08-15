from dataclasses import dataclass, field


@dataclass
class Character:
    name: str = "name"
    voice_id: str = ""
    gender: str = "m"
    description: str | None = ""

    def __post_init__(self) -> None:
        if self.gender not in ("m", "f"):
            raise ValueError("gender must be 'm' or 'f'")


@dataclass
class Group:
    group: str = ""
    description: str | None = None
    characters: list[Character] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.characters)
    def __post_init__(self) -> None:
        if self.group is None:
            self.group = ""


@dataclass
class Configuration:
    # folders
    input_folder: str = "scenario"
    output_folder: str = "voices"
    # app
    debug: bool = True
    converter: str = "dev"
    # elevenlabs
    elevenlabs_api_key: str = "no_key"
    catalogue_size: int = 100
    # dev
    female_voice_id: str = "default"
    male_voice_id: str = "default"
