from textual.app import (
    App,
    ComposeResult,
)
from textual.containers import Container
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
)

from music import MusicClient

from .library import LibraryScreen
from .statistics import StatsScreen
from .tagging import TaggingScreen


class TaggingApp(App):
    """Main Tagging Application."""

    CSS_PATH = "css/index.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "select_item", "Select"),
    ]

    def __init__(self) -> None:
        """Initialize class instance."""
        super().__init__()
        self.client = MusicClient()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            ListView(
                ListItem(Label("Add tags"), id="tagging"),
                ListItem(Label("Library"), id="library"),
                ListItem(Label("Statistics"), id="statistics"),
                id="main_menu",
            ),
            id="main_container",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.handle_selection(event.item.id)

    def action_select_item(self) -> None:
        # This handles Enter key press
        list_view = self.query_one(ListView)
        if list_view.index is not None:  # Check if an item is highlighted
            selected_item = list_view.children[list_view.index]
            self.handle_selection(selected_item.id)

    def handle_selection(self, item_id: str | None) -> None:
        # Common handler for both selection methods
        if item_id == "statistics":
            self.push_screen(StatsScreen())
        elif item_id == "library":
            self.push_screen(LibraryScreen())
        elif item_id == "tagging":
            self.push_screen(TaggingScreen())
        else:
            raise ValueError("invalid id")


if __name__ == "__main__":
    app = TaggingApp()
    app.run()
