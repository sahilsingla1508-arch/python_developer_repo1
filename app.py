import sqlite3
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Slider, SelectionList
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding

from code_viewer import CodeViewer
from variable_panel import VariablePanel
from timeline import TimelineWidget
from watchlist_panel import WatchlistPanel

class PyChronicleUI(App):
    """PyChronicle Hacker-Style TUI Application Shell."""
    CSS_PATH = "styles.tcss"
    
    # Keybindings for terminal control
    BINDINGS = [
        Binding("q", "quit", "Quit App", show=True),
        Binding("left", "step_backward", "Step -1", show=True),
        Binding("right", "step_forward", "Step +1", show=True),
        Binding("w", "focus_watchlist", "Toggle Watchlist", show=True),
    ]

    current_event_id = reactive(1)
    watched_filters = reactive(list)

    def __init__(self, target_script: str, db_path: str = "chronicle.db", **kwargs):
        super().__init__(**kwargs)
        self.target_script = target_script
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="workspace"):
            with Vertical(id="code-container"):
                yield Static(f"💻 TARGET: {self.target_script}", classes="pane-title")
                yield CodeViewer(file_path=self.target_script, id="code-pane")
            with Vertical(id="inspector-container"):
                yield Static("🔍 DELTA STATE INSPECTOR", classes="pane-title")
                yield VariablePanel(id="var-inspector")
            with Vertical(id="watchlist-container"):
                yield Static("👁️ WATCH VARIABLES", classes="pane-title")
                yield WatchlistPanel(target_script=self.target_script, id="watchlist-pane")
        
        yield TimelineWidget(db_path=self.db_path, id="timeline-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "PyChronicle Debugger v0.4"
        watchlist = self.query_one("#watchlist-pane", WatchlistPanel)
        self.watched_filters = watchlist.detected_vars
        self.refresh_ui()

    def on_slider_changed(self, event: Slider.Changed) -> None:
        if event.slider.id == "timeline-slider":
            self.current_event_id = event.value

    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        if event.selection_list.id == "watchlist-pane":
            self.watched_filters = event.selected

    def action_step_backward(self) -> None:
        slider = self.query_one("#timeline-slider", Slider)
        if slider.value > slider.min:
            slider.value -= 1

    def action_step_forward(self) -> None:
        slider = self.query_one("#timeline-slider", Slider)
        if slider.value < slider.max:
            slider.value += 1

    def action_focus_watchlist(self) -> None:
        self.query_one("#watchlist-pane", WatchlistPanel).focus()

    def watch_current_event_id(self, new_id: int) -> None:
        self.refresh_ui()

    def watch_watched_filters(self, new_filters: list) -> None:
        self.refresh_ui()

    def refresh_ui(self):
        """Reconstructs state delta history from SQLite up to the selected step."""
        new_id = self.current_event_id
        line_to_highlight = 1
        historical_variables = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT line_number FROM state_log WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            if row:
                line_to_highlight = row[0]

            # Reconstruct delta state
            cursor.execute(
                "SELECT variable_name, serialized_value FROM state_log WHERE id <= ? ORDER BY id ASC",
                (new_id,)
            )
            for name, val in cursor.fetchall():
                historical_variables[name] = val
            conn.close()
        except Exception:
            pass

        try:
            self.query_one("#code-pane", CodeViewer).highlight_line(line_to_highlight)
            self.query_one("#var-inspector", VariablePanel).update_state(
                historical_variables, 
                self.watched_filters
            )
            self.sub_title = f"Step Tick: {new_id} | Active Line: {line_to_highlight}"
        except Exception:
            pass
