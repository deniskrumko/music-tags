from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Static,
)


class StatsScreen(Screen):
    """Statistics screen showing sample stats."""

    BINDINGS = [
        ("q", "quit_screen", "Back to Menu"),
    ]

    def action_quit_screen(self) -> None:
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Label("Sample Statistics", classes="heading"),
            Static("Total Files: 324"),
            Static("Tagged Files: 187"),
            Static("Untagged Files: 137"),
            Static("Most Common Tag: 'important' (42 files)"),
            Static("Average Tags Per File: 2.3"),
            Button("Back to Main Menu", id="back_button"),
            id="stats_container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()
