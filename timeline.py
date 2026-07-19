import sqlite3
from textual.widgets import Slider, Static
from textual.containers import Horizontal

class TimelineWidget(Horizontal):
    """
    Orchestrates the time-scrubbing interface.
    Calculates event density from the backend database structure.
    """
    def __init__(self, db_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path
        self.max_events = self._get_total_events()

    def _get_total_events(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            res = cursor.fetchone()
            conn.close()
            return res[0] if res and res[0] > 0 else 1
        except Exception:
            return 1

    def compose(self):
        yield Static("⏱️ Timeline Index: ", id="timeline-label")
        yield Slider(min=1, max=self.max_events, step=1, value=1, id="timeline-slider")
