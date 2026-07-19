from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label
from textual.widget import Widget

# Textual versions differ slightly. This import works for recent versions.
from textual.widgets import Slider


class TimelineWidget(Widget):
    """
    Timeline Slider Placeholder

    Day 4 Task:
    Displays a slider with a fixed range (0-10).
    No backend integration yet.
    """

    def compose(self) -> ComposeResult:

        yield Vertical(

            Label(
                "Execution Timeline",
                id="timeline_title"
            ),

            Slider(
                min=0,
                max=10,
                value=0,
                id="timeline_slider"
            ),

            Label(
                "Current Frame : 0",
                id="timeline_value"
            ),
        )

    def on_slider_changed(self, event: Slider.Changed) -> None:
        """Update the displayed slider value."""

        self.query_one("#timeline_value", Label).update(
            f"Current Frame : {int(event.value)}"
        )
