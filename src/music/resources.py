from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

MACOS_DS_STORE = ".DS_Store"
LOGIC_PRO_EXT = ".logicx"
AUDIO_FILE_EXT = {".wav", ".mp3", ".mp4", ".m4a"}
IMAGE_FILE_EXT = {".png", ".jpg", ".psd", ".webp"}
GUITAR_PRO_EXT = {".gp", ".gpx", ".gp4", ".gp5"}


@dataclass
class MusicFile:
    path: Path

    def __repr__(self) -> str:
        return f"<MusicFile: {self.name}>"

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def ext(self) -> str:
        return "." + str(self.name.rsplit(".", maxsplit=1)[1])

    @property
    def is_audio(self) -> bool:
        return self.ext in AUDIO_FILE_EXT

    @property
    def is_gtp(self) -> bool:
        return self.ext in GUITAR_PRO_EXT

    @property
    def is_logicx(self) -> bool:
        return self.ext == LOGIC_PRO_EXT

    @property
    def is_other(self) -> bool:
        return not any(
            [
                self.is_audio,
                self.is_gtp,
                self.is_logicx,
            ],
        )


@dataclass
class RootDir:
    name: str
    path: Path
    ignored_dirs: list[str] | None = None
    ignored_files: list[str] | None = None


@dataclass
class MusicDir:
    path: Path
    root_dir: RootDir

    @property
    def name(self) -> str:
        """Directory name."""
        return self.path.name

    @property
    def parent_dir(self) -> Path:
        """Path relative to root dir"""
        return self.path.parent

    @cached_property
    def name_without_tags(self) -> str:
        name = self.name.split("(")[0]
        return " ".join(p for p in name.split() if not p.startswith("#"))

    @property
    def name_tags(self) -> list[str]:
        if "(" not in self.name:
            return []

        tags = self.name.split("(")[1]
        tags = tags.split(")")[0]

        if ":" in tags:
            tags = " ".join(tags.split(":"))

        return [t.lower().strip().rstrip(",") for t in tags.split()]

    @property
    def audio_files(self) -> list[MusicFile]:
        return [f for f in self.files if f.is_audio]

    @property
    def gtp_files(self) -> list[MusicFile]:
        return [f for f in self.files if f.is_gtp]

    @property
    def logicx_files(self) -> list[MusicFile]:
        return [f for f in self.files if f.is_logicx]

    @property
    def other_files(self) -> list[MusicFile]:
        return [f for f in self.files if f.is_other]

    @cached_property
    def files(self) -> list[MusicFile]:
        def crawl(directory: Path) -> list[MusicFile]:
            result = []
            for f in directory.iterdir():
                if f.is_file() and f.name != MACOS_DS_STORE:
                    result.append(MusicFile(path=f))
                elif f.is_dir():
                    if f.name.endswith(LOGIC_PRO_EXT):
                        result.append(MusicFile(path=f))
                    else:
                        result.extend(crawl(f))

            return result

        return crawl(self.path)
