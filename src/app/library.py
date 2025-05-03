import subprocess

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
)

from music import MusicClient
from music.directories import (
    MusicDir,
    MusicFileType,
)


class LibraryScreen(Screen):
    """Library screen showing a table of items."""

    COLUMNS = [
        ("Name", "name"),
        ("Audio", "audio"),
        ("LogicX", "logicx"),
        ("GTP", "gtp"),
        ("Other", "other"),
        ("Path", "path"),
    ]

    BINDINGS = [
        ("q", "quit_screen", "Back to Menu"),
        ("n", "sort_by_name", "Name"),
        ("a", "sort_by_audio", "Audio"),
        ("l", "sort_by_logicx", "LogicX"),
        ("o", "sort_by_other", "Other"),
        ("g", "sort_by_gtp", "GTP"),
        ("f", "open_in_finder", "Open in Finder"),
    ]

    def __init__(self) -> None:
        """Initialize class instance."""
        super().__init__()
        self.client = MusicClient()
        self.current_sorts: set = set()

    # Sorting actions

    def action_sort_by_name(self) -> None:
        self._sort_column("name")

    def action_sort_by_audio(self) -> None:
        self._sort_column("audio")

    def action_sort_by_logicx(self) -> None:
        self._sort_column("logicx")

    def action_sort_by_gtp(self) -> None:
        self._sort_column("gtp")

    def action_sort_by_other(self) -> None:
        self._sort_column("other")

    def _sort_column(self, name: str) -> None:
        dt = self.query_one(DataTable)
        reverse = self.sort_reverse(name)
        dt.sort(name, reverse=reverse)

        self.app.notify(
            title=f"Sorted by {name} column",
            message="Descending" if reverse else "Ascending",
        )

    def sort_reverse(self, sort_type: str) -> bool:
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_quit_screen(self) -> None:
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="library_table")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Library"

        # Set up the table
        table = self.query_one(DataTable)

        for label, key in self.COLUMNS:
            text = Text(label)
            text.stylize("bold yellow", 0, 1)
            table.add_column(text, key=key)

        self.mdirs: list[MusicDir] = sorted(
            self.client.find_music_dirs(),
            key=lambda mdir: mdir.name_without_tags,
        )

        self.mdirs_index: dict[str, int] = {}

        for i, mdir in enumerate(self.mdirs, start=1):
            root_dir = mdir.root_dir
            folder = mdir.parent_dir.relative_to(root_dir.path)
            colored_path = Text(f"{root_dir.name}/{folder}")
            colored_path.stylize("yellow", 0, len(root_dir.name))

            self.mdirs_index[mdir.name_without_tags] = i - 1

            table.add_row(
                mdir.name_without_tags,
                mdir.count_files(MusicFileType.AUDIO),
                mdir.count_files(MusicFileType.LOGIC_X),
                mdir.count_files(MusicFileType.GUITAR_PRO),
                mdir.count_files(MusicFileType.OTHER),
                colored_path,
                label=str(i),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()

    def action_open_in_finder(self) -> None:
        """Open the directory of the selected row in Finder."""
        dt = self.query_one(DataTable)

        name_without_tags = dt.get_row_at(dt.cursor_row)[0]

        # Get the music directory corresponding to the selected row
        index = self.mdirs_index[name_without_tags]
        selected_mdir = self.mdirs[index]

        # Get the path from the selected music directory
        path = selected_mdir.path

        try:
            subprocess.run(["open", path], check=True)
            self.notify(f"Opening in Finder: {selected_mdir.name}")
        except subprocess.SubprocessError:
            self.notify("Failed to open in Finder")
