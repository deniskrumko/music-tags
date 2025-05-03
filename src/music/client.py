from functools import cached_property
from pathlib import Path
from typing import Iterator

import toml

from .directories import (
    IGNORED_FILES,
    LOGICX_EXT,
    MusicDir,
    RootDir,
)
from .tags import (
    Tag,
    TagOptions,
)


class MusicClient:

    def __init__(self, config_path: str = "config/local.toml"):
        """Initialize class instance."""
        self.config_path = config_path

    def show_music_dir_tags(self) -> None:
        """Show all unique tags located in music dir name (usually in brackets)."""
        result = set()
        for mdir in self.find_music_dirs():
            result.update(set(mdir.name_tags))

        for i, tag in enumerate(sorted(result)):
            print(f"{i}. {tag}")
            if i % 10 == 0:
                print()

    def find_music_dirs(self) -> Iterator[MusicDir]:
        """Locate all music directories that contain at least one file."""
        for params in self.config["root_dir"].values():
            params["path"] = Path(params["path"])
            root_dir = RootDir(**params)

            yield from self.find_music_dir(
                path=root_dir.path,
                root_dir=root_dir,
                ignored_dirs=root_dir.ignored_dirs,
                ignored_files=root_dir.ignored_files,
            )

    def find_music_dir(
        self,
        path: Path,
        root_dir: RootDir,
        ignored_dirs: list[str] | None = None,
        ignored_files: list[str] | None = None,
    ) -> Iterator[MusicDir]:
        """Recursively crawl directory and yield music directories."""
        items = list(path.iterdir())
        files = [f for f in items if self.is_file(f, ignored_files)]
        dirs = [d for d in items if self.is_dir(d, ignored_dirs)]

        if files:
            # If directory has files, yield it and don't go deeper
            yield MusicDir(
                path=Path(path),
                root_dir=root_dir,
            )
        elif dirs:
            # If directory has no files but has subdirs, check them
            for dir_name in dirs:
                yield from self.find_music_dir(
                    path=dir_name,
                    root_dir=root_dir,
                    ignored_dirs=ignored_dirs,
                    ignored_files=ignored_files,
                )

    def is_dir(
        self,
        path: Path,
        ignored_dirs: list[str] | None = None,
    ) -> bool:
        if path.name.endswith(LOGICX_EXT):
            return False

        if ignored_dirs and path.name in ignored_dirs:
            return False

        return path.is_dir()

    def is_file(
        self,
        path: Path,
        ignored_files: list[str] | None = None,
    ) -> bool:
        if path.name in IGNORED_FILES:
            return False

        if ignored_files and path.name in ignored_files:
            return False

        return path.is_file()

    @cached_property
    def config(self) -> dict:
        return dict(toml.load(self.config_path))

    @cached_property
    def tag_options(self) -> TagOptions:
        return {
            tag_name: Tag(name=tag_name, **options)
            for tag_name, options in self.config["tag"].items()
        }


if __name__ == "__main__":
    app = MusicClient()
    app.tag_options
