import sqlite3
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Slider
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

# Import custom modular widgets
from code_viewer import CodeViewer
from variable_panel import VariablePanel
from timeline import TimelineWidget

class PyChronicleUI(App):
    """Core UI Application Orchestrator linking the layout windows."""
    CSS_PATH = "styles.tcss"
    current_event_id = reactive(1)

    def __init__(self, target_script: str, db_path: str = "chronicle.db", **kwargs):
        super().__init__(**kwargs)
        self.target_script = target_script
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="workspace"):
            with Vertical(id="code-container"):
                yield Static(f"💻 LIVE RUN ARCHITECTURE: {self.target_script}", classes="pane-title")
                yield CodeViewer(file_path=self.target_script, id="code-pane")
            with Vertical(id="inspector-container"):
                yield Static("🔍 DELTA VARIABLE HISTORY TRACKER", classes="pane-title")
                yield VariablePanel(id="var-inspector")
        
        # Inject modularized Timeline component
        yield TimelineWidget(db_path=self.db_path, id="timeline-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "PyChronicle Debugger"
        self.refresh_ui()

    def on_slider_changed(self, event: Slider.Changed) -> None:
        if event.slider.id == "timeline-slider":
            self.current_event_id = event.value

    def watch_current_event_id(self, new_id: int) -> None:
        self.refresh_ui()

    def refresh_ui(self):
        new_id = self.current_event_id
        line_to_highlight = 1
        historical_variables = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT line_number FROM events WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            if row:
                line_to_highlight = row[0]

            cursor.execute(
                "SELECT variable_name, serialized_value FROM events WHERE id <= ? ORDER BY id ASC",
                (new_id,)
            )
            for name, val in cursor.fetchall():
                historical_variables[name] = val
            conn.close()
        except Exception:
            pass

        try:
            self.query_one("#code-pane", CodeViewer).highlight_line(line_to_highlight)
            self.query_one("#var-inspector", VariablePanel).update_state(historical_variables)
            self.sub_title = f"Step Mutation: {new_id} | Highlighted Line: {line_to_highlight}"
        except Exception:
            pass
