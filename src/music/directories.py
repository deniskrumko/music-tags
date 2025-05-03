from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .files import (
    IGNORED_FILES,
    LOGICX_EXT,
    MusicFile,
    MusicFileType,
)
from .tags import (
    TAG_FILE,
    MusicDirTags,
    TagOptions,
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
    def is_tagged(self) -> bool:
        return (self.path / TAG_FILE).exists()

    def get_tags(self, tag_options: TagOptions) -> MusicDirTags:
        return MusicDirTags.from_music_dir(self.path, tag_options)

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

    def get_files(self, file_type: MusicFileType) -> list[MusicFile]:
        return [f for f in self.files if f.file_type == file_type]

    def count_files(self, file_type: MusicFileType) -> int:
        return len(self.get_files(file_type))

    @cached_property
    def files(self) -> list[MusicFile]:
        def crawl(directory: Path) -> list[MusicFile]:
            result = []
            for f in directory.iterdir():
                if f.is_file() and f.name not in IGNORED_FILES:
                    result.append(MusicFile(path=f))
                elif f.is_dir():
                    if f.name.endswith(LOGICX_EXT):
                        result.append(MusicFile(path=f))
                    else:
                        result.extend(crawl(f))

            return result

        return crawl(self.path)
