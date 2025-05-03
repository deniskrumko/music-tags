from dataclasses import dataclass
from pathlib import Path
from typing import Union

# Tagging
TAG_FILE = "music_tag.txt"
TAG_FILE_DESCRIPTION_SEPARATOR = "--- Music Description ---"
TAG_FILE_LIST_SEPARATOR = ","
TAG_FILE_KEY_VALUE_SEPARATOR = "="

TagValue = Union[str, list[str]]


@dataclass
class Tag:
    name: str
    values: list[str]
    default: str | None = None
    multiselect: bool = False
    required: bool = False

    def __repr__(self) -> str:
        return f"<Tag: {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)


TagOptions = dict[str, Tag]


@dataclass
class MusicDirTags:
    path: Path
    tags: dict[Tag, TagValue]
    description: str

    def is_selected(self, tag: Tag, value: str) -> bool:
        current_value = self.tags[tag]
        if isinstance(current_value, str):
            return value == current_value
        elif isinstance(current_value, list):
            return value in current_value
        else:
            raise TypeError(f"tag value has incompatible type: {type(current_value)}")

    @classmethod
    def from_file(cls, file_path: Path, tag_options: TagOptions) -> "MusicDirTags":
        tags: dict[Tag, TagValue] = {}
        description = ""

        with open(file_path, "r") as f:
            description_started = False
            for line in f.readlines():
                line = line.strip()

                if line == TAG_FILE_DESCRIPTION_SEPARATOR:
                    description_started = True
                elif description_started:
                    description += line
                else:
                    value_list = None
                    key, value = line.split(TAG_FILE_KEY_VALUE_SEPARATOR)

                    if TAG_FILE_LIST_SEPARATOR in value:
                        value_list = value.split(TAG_FILE_LIST_SEPARATOR)

                    tag = tag_options.get(key)
                    if not tag:
                        raise ValueError(f"Tag with name {key} not found")

                    tags[tag] = value_list or value

        return cls(
            path=file_path,
            tags=tags,
            description=description,
        )

    def to_file(self) -> None:
        with open(self.path, "w") as f:
            for k, v in self.tags.items():
                if isinstance(v, list):
                    v = TAG_FILE_LIST_SEPARATOR.join(v)
                f.write(f"{k}{TAG_FILE_KEY_VALUE_SEPARATOR}{v}\n")

            if self.description:
                f.write(f"{TAG_FILE_DESCRIPTION_SEPARATOR}\n{self.description}\n")

    @classmethod
    def from_music_dir(cls, music_dir_path: Path, tag_options: TagOptions) -> "MusicDirTags":
        return cls.from_file(
            file_path=music_dir_path / TAG_FILE,
            tag_options=tag_options,
        )
