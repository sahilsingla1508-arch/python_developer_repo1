from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Slider

from storage.storage import get_event_count


class TimelineWidget(Widget):
    """
    Timeline slider connected to the number of events
    stored in SQLite.
    """

    def __init__(self):
        super().__init__()

        self.event_count = get_event_count()

        if self.event_count <= 0:
            self.event_count = 1

    def compose(self) -> ComposeResult:

        yield Label(
            "Execution Timeline",
            id="timeline_title"
        )

        yield Slider(
            min=0,
            max=self.event_count - 1,
            value=0,
            id="timeline_slider"
        )

        yield Label(
            f"Current Event : 0 / {self.event_count - 1}",
            id="timeline_value"
        )

    def on_slider_changed(self, event: Slider.Changed) -> None:

        index = int(event.value)

        self.query_one("#timeline_value", Label).update(
            f"Current Event : {index} / {self.event_count - 1}"
        )

        # Placeholder for future synchronization with
        # code viewer and variable panel.
        self.post_message(self.EventSelected(index))

    class EventSelected(Widget.Message):
        """
        Message emitted whenever the timeline changes.
        """

        def __init__(self, index: int):
            super().__init__()
            self.index = index
