from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path

# Files
IGNORED_FILES = {".DS_Store"}

# Extensions
LOGICX_EXT = ".logicx"
AUDIO_FILE_EXT = {".wav", ".mp3", ".mp4", ".m4a"}
IMAGE_FILE_EXT = {".png", ".jpg", ".psd", ".webp"}
GUITAR_PRO_EXT = {".gp", ".gpx", ".gp4", ".gp5"}


class MusicFileType(Enum):
    """Enum with music file types."""

    LOGIC_X = "logicx"
    AUDIO = "audio"
    IMAGE = "image"
    GUITAR_PRO = "gpt"
    OTHER = "other"

    @property
    def emoji(self) -> str:
        return {
            self.LOGIC_X.name: "📚",
            self.AUDIO.name: "🎵",
            self.IMAGE.name: "🌄",
            self.GUITAR_PRO.name: "🎸",
            self.OTHER.name: "📄",
        }[self.name]

    @classmethod
    def from_ext(cls, ext: str) -> "MusicFileType":
        if ext == LOGICX_EXT:
            return cls.LOGIC_X

        if ext in AUDIO_FILE_EXT:
            return cls.AUDIO

        if ext in IMAGE_FILE_EXT:
            return cls.IMAGE

        if ext in GUITAR_PRO_EXT:
            return cls.GUITAR_PRO

        return cls.OTHER


@dataclass
class MusicFile:
    path: Path

    def __repr__(self) -> str:
        return f"<MusicFile: {self.name}>"

    @classmethod
    def from_string(cls, path: str) -> "MusicFile":
        return cls(path=Path(path))

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def ext(self) -> str:
        """Return file extension with dot or empty string if it's directory."""
        if "." not in self.name:
            return ""

        return "." + str(self.name.rsplit(".", maxsplit=1)[1])

    @cached_property
    def file_type(self) -> MusicFileType:
        return MusicFileType.from_ext(self.ext)

    @property
    def is_logicx(self) -> bool:
        return self.file_type == MusicFileType.LOGIC_X
