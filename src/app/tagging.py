import os
import subprocess

from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Label,
    Tree,
)


class TaggingScreen(Screen):
    """Tagging screen with directory tree and tag checkboxes."""

    BINDINGS = [
        ("o", "open_in_finder", "Open in Finder"),
        ("q", "quit_screen", "Back to Menu"),
        ("n", "next_item", "Next Item"),
    ]

    current_path = os.path.expanduser("~/Documents")  # Default path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("File Tagging", classes="heading")

        with Horizontal():
            # Left side - directory tree
            with Vertical(id="tree_container"):
                yield Label("Directory Structure")
                yield Tree("Documents", id="directory_tree")

            # Right side - tag checkboxes
            with Vertical(id="tags_container"):
                yield Label("Available Tags")
                yield Checkbox("Important", value=False)
                yield Checkbox("Work", value=False)
                yield Checkbox("Personal", value=False)
                yield Checkbox("Urgent", value=False)
                yield Checkbox("Draft", value=False)
                yield Checkbox("Final", value=False)
                yield Checkbox("Reference", value=False)
                yield Button("Save Tags", id="save_button")
                yield Button("Next Item", id="next_button")

        yield Button("Back to Main Menu", id="back_button")
        yield Footer()

    def on_mount(self) -> None:
        # Set up the directory tree
        self._populate_tree()

    def _populate_tree(self) -> None:
        tree = self.query_one("#directory_tree", Tree)
        tree.root.expand()

        # Add sample directories and files
        docs = tree.root.add("Documents", expand=True)
        work = docs.add("Work", expand=True)
        work.add_leaf("Project A")
        work.add_leaf("Project B")
        work.add_leaf("Meeting Notes.txt")

        personal = docs.add("Personal", expand=True)
        personal.add_leaf("Finances")
        personal.add_leaf("Travel")
        personal.add_leaf("Photos")

    def action_open_in_finder(self) -> None:
        # Open the current directory in macOS Finder
        tree = self.query_one("#directory_tree", Tree)
        if tree.cursor_node:
            path = self.current_path
            try:
                subprocess.run(["open", path], check=True)
                self.notify("Opening in Finder: " + path)
            except subprocess.SubprocessError:
                self.notify("Failed to open in Finder")

    def action_quit_screen(self) -> None:
        self.app.pop_screen()

    def action_next_item(self) -> None:
        self.notify("Moving to next item")
        # In a real app, you would save current state and load the next item
        # For now, just reset the checkboxes
        for checkbox in self.query(Checkbox):
            checkbox.value = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()
        elif event.button.id == "save_button":
            self.notify("Tags saved!")
        elif event.button.id == "next_button":
            self.action_next_item()
