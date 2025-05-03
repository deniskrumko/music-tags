import os
import subprocess

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    RadioButton,
    RadioSet,
    SelectionList,
    TextArea,
)
from textual.widgets.selection_list import Selection

from music import (
    MusicClient,
    MusicDir,
    MusicDirTags,
    MusicFileType,
    Tag,
)

from .widgets import MusicDirectoryTree


class TaggingScreen(Screen):
    """Tagging screen with directory tree and tag checkboxes."""

    CSS = """
    DirectoryTree, SelectionList, RadioSet, Button, #info {
        padding: 0 1;
        border: round orange;
        background: $background;
    }

    Button {
        border: round orange;
        background: $background;
    }

    RadioSet, #info {
        width: 100%;
    }

    VerticalScroll, Vertical {
        background: $background;
    }

    #tags_container {
        margin-left: 1;
    }

    #buttons {
        height: 3;
    }
    """

    BINDINGS = [
        ("q", "quit_screen", "Back to Menu"),
        ("f", "open_in_finder", "Open in Finder"),
        ("s", "save_changes", "Save"),
        ("p", "prev_item", "Prev"),
        ("n", "next_item", "Next"),
    ]

    current_path = os.path.expanduser("~/Documents")  # Default path

    def __init__(
        self,
        current_index: int = 0,
        edit_mode: bool = True,
    ) -> None:
        """Initialize class instance."""
        super().__init__()
        self.client = MusicClient()
        self.music_dirs = list(self.client.find_music_dirs())
        self.current_index = current_index
        self.edit_mode = edit_mode
        self.changed = False

    @property
    def music_dir(self) -> MusicDir:
        return self.music_dirs[self.current_index]

    @property
    def music_dir_tags(self) -> MusicDirTags:
        return self.music_dir.get_tags(self.client.tag_options)

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            with Vertical(id="tree_container"):
                yield from self.compose_info()

                tree = MusicDirectoryTree(
                    self.music_dir.path,
                    id="directory_tree",
                )
                tree.border_title = "Tree"
                yield tree

                with Horizontal(id="buttons"):
                    yield Button("Save and continue", id="save_and_continue")
                    yield Button("Discard", id="discard_changes")

            with VerticalScroll(id="tags_container"):
                yield from self.compose_tags()

        yield Footer()

    def compose_info(self) -> ComposeResult:
        text = Text()
        if self.music_dir.is_tagged:
            text.append("Tagged", "bold green")
        else:
            text.append("Untagged", "bright_black")

        for file_type in MusicFileType:
            count = self.music_dir.count_files(file_type)
            if count:
                text.append(f"  {file_type.name}:", "bold bright_cyan")
                text.append(f"{count}", "bright_cyan")

        info = Label(text, id="info")
        info.border_title = self.music_dir.name
        yield info

    def compose_tags(self) -> ComposeResult:
        for tag_name, tag in self.client.tag_options.items():
            obj: Widget

            if tag.multiselect:
                obj = self.compose_selection_list(tag)
            else:
                obj = self.compose_radio_set(tag)

            obj.border_title = tag_name
            yield obj

        text = ""
        if self.music_dir.is_tagged:
            text = self.music_dir_tags.description

        yield TextArea(
            text=text,
            id="description",
        )

    def compose_selection_list(self, tag: Tag) -> SelectionList:
        selections: list[Selection]

        if self.music_dir.is_tagged:
            selections = [
                Selection(value, i, self.music_dir_tags.is_selected(tag, value))
                for i, value in enumerate(tag.values)
            ]
        else:
            selections = [
                Selection(value, i, value == tag.default) for i, value in enumerate(tag.values)
            ]

        return SelectionList[int](
            *selections,
            id=f"tag_{tag.name}",
            disabled=not self.edit_mode,
        )

    def compose_radio_set(self, tag: Tag) -> RadioSet:
        buttons: list[RadioButton]

        if self.music_dir.is_tagged:
            buttons = [
                RadioButton(v, value=self.music_dir_tags.is_selected(tag, v)) for v in tag.values
            ]
        else:
            buttons = [RadioButton(v, value=(v == tag.default)) for v in tag.values]

        return RadioSet(
            *buttons,
            id=f"tag_{tag.name}",
            disabled=not self.edit_mode,
        )

    def on_mount(self) -> None:
        self.sub_title = "Tagging"
        scroll = self.query_one("#tags_container")
        scroll.focus()

    def on_radio_set_changed(self, pressed: RadioButton) -> None:
        self.changed = True

    def on_selection_list_selected_changed(self, message: SelectionList.SelectedChanged) -> None:
        self.changed = True

    def action_open_in_finder(self) -> None:
        # Open the current directory in macOS Finder
        tree = self.query_one("#directory_tree")
        if tree.cursor_node:
            path = str(self.music_dir.path)
            try:
                subprocess.run(["open", path], check=True)
            except subprocess.SubprocessError:
                self.notify("Failed to open in Finder")

    def action_quit_screen(self) -> None:
        self.app.pop_screen()

    def action_next_item(self) -> None:
        self.go_to_index(self.current_index + 1)

    def action_prev_item(self) -> None:
        self.go_to_index(self.current_index - 1)

    def action_save_changes(self) -> None:
        self.notify(f"Saved tags for {self.music_dir.name}")
        self.changed = False

    def go_to_index(self, index: int, force: bool = False) -> None:
        if self.changed and not force:
            self.notify("You have unsaved changes", severity="error")
            return

        new_screen = self.__class__(current_index=index)
        self.app.switch_screen(new_screen)

    def save_and_continue(self) -> None:
        self.action_save_changes()
        self.action_next_item()

    def discard_changes(self) -> None:
        self.go_to_index(self.current_index, force=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_and_continue":
            self.save_and_continue()
        elif event.button.id == "discard_changes":
            self.discard_changes()
