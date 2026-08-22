import sqlite3

from textual.app import App, ComposeResult
from textual.widgets import Static, SelectionList
from textual_slider import Slider
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive

# Import custom modular widgets
from code_viewer import CodeViewer
from variable_panel import VariablePanel
from timeline import TimelineWidget
from watchlist_panel import WatchlistPanel


# ── System Status Panel ───────────────────────────────────────────────────────

class SystemStatusPanel(Static):
    """
    Real-time system health display for PyChronicle.

    Shows green ● indicators for AST, Tracer, and SQLite subsystems,
    plus live event count and step counter matching reference UI.
    """

    def __init__(self, **kwargs):
        initial = (
            "● AST READY  ● TRACER READY  ● SQLITE READY\n"
            "EVENTS: —  ·  STEP: — / —"
        )
        super().__init__(initial, **kwargs)
        self._event_count = 0
        self._step = 1
        self._total = 1

    def on_mount(self) -> None:
        self._draw_status()

    def update_status(self, event_count: int, step: int, total: int) -> None:
        """Refresh all status indicators with the latest execution state."""
        self._event_count = event_count
        self._step = step
        self._total = total
        self._draw_status()

    def _draw_status(self) -> None:
        step_str = f"{self._step} / {self._total}"
        self.update(
            "[bold #3fb950]●[/] [bold #3fb950]AST[/] [bold #3fb950]READY[/]  "
            "[bold #3fb950]●[/] [bold #3fb950]TRACER[/] [bold #3fb950]READY[/]  "
            "[bold #3fb950]●[/] [bold #3fb950]SQLITE[/] [bold #3fb950]READY[/]\n"
            f"[dim #8b949e]EVENTS:[/] [bold #e3b341]{self._event_count}[/]  ·  "
            f"[dim #8b949e]STEP:[/] [bold #58a6ff]{step_str}[/]"
        )



# ── Main Application ──────────────────────────────────────────────────────────

class PyChronicleUI(App):
    """Core UI Application Orchestrator matching reference PyChronicle design."""

    CSS_PATH = "styles.tcss"

    # ── Keyboard bindings ─────────────────────────────────────────────────────
    BINDINGS = [
        ("q",     "quit",        "Quit"),
        ("left",  "step_prev",   "Prev"),
        ("right", "step_next",   "Next"),
        ("p",     "toggle_play", "Play/Stop"),
        ("r",     "replay",      "Replay"),
    ]

    current_event_id = reactive(1)

    def __init__(
        self,
        target_script: str,
        db_path: str = "chronicle.db",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target_script = target_script
        self.db_path = db_path
        self._total_events = self._fetch_total_events()
        # None means the watchlist has not been initialized yet.
        self.watched_variables = None

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _fetch_total_events(self) -> int:
        """Read total event count from DB for display in the header."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                res = conn.execute("SELECT COUNT(*) FROM events").fetchone()
                return res[0] if res and res[0] > 0 else 1
        except Exception:
            return 1

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        # ── Top Header ────────────────────────────────────────────────────────
        with Horizontal(id="app-header"):
            yield Static("PyChronicle", id="header-brand")
            yield Static("|", id="header-separator")
            yield Static("AST-Powered Time-Travel Debugger", id="header-tagline")
            yield Static(f"⏱  Step 1 / {self._total_events}", id="header-step")

        # ── Main Workspace ────────────────────────────────────────────────────
        with Horizontal(id="workspace"):

            # Left Column: Source Code Viewer
            with Vertical(id="code-container"):
                yield Static(
                    f"SOURCE CODE  ›  {self.target_script}",
                    classes="pane-title",
                )
                with ScrollableContainer(id="code-scroll"):
                    yield CodeViewer(file_path=self.target_script, id="code-pane")


            # Right Sidebar: Variable Inspector + Watchlist + System Status
            with Vertical(id="right-sidebar"):

                yield Static("VARIABLE INSPECTOR", classes="pane-title")
                yield VariablePanel(id="var-inspector")

                yield Static("WATCH VARIABLES", classes="pane-title-secondary")
                yield WatchlistPanel(target_script=self.target_script, id="watchlist")

                yield Static("SYSTEM STATUS", classes="pane-title-status")
                yield SystemStatusPanel(id="status-panel")

        # ── Execution Timeline Strip ──────────────────────────────────────────
        yield TimelineWidget(db_path=self.db_path, id="timeline-panel")

        # ── Footer Bar ────────────────────────────────────────────────────────
        with Horizontal(id="app-footer"):
            yield Static(
                "[bold #58a6ff]q[/] Quit    "
                "[bold #58a6ff]p[/] Play/Stop    "
                "[bold #58a6ff]r[/] Replay    "
                "[bold #58a6ff]←[/] Prev    "
                "[bold #58a6ff]→[/] Next",
                id="footer-keys"
            )
            yield Static(
                f"Script: [bold #58a6ff]{self.target_script}[/]",
                id="footer-script"
            )

    # ── Mount ─────────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self.title = "PyChronicle"
        self.sub_title = "AST-Powered Time-Travel Debugger"

        # Initially all variables are selected by WatchlistPanel.
        try:
            watchlist = self.query_one("#watchlist", WatchlistPanel)
            self.watched_variables = set(watchlist.get_selected_variables())
        except Exception:
            self.watched_variables = set()

        self.refresh_ui()

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_selection_list_selection_toggled(
        self,
        event: SelectionList.SelectionToggled,
    ) -> None:
        """Called whenever a variable is checked/unchecked in the Watchlist."""
        if event.selection_list.id != "watchlist":
            return
        watchlist = self.query_one("#watchlist", WatchlistPanel)
        self.watched_variables = set(watchlist.get_selected_variables())
        self.refresh_ui()

    def on_slider_changed(self, event: Slider.Changed) -> None:
        self.current_event_id = int(event.value)

    def watch_current_event_id(self, new_id: int) -> None:
        self.refresh_ui()

    # ── Keyboard actions ──────────────────────────────────────────────────────

    def action_step_prev(self) -> None:
        """Move one step back in the timeline."""
        try:
            timeline = self.query_one("#timeline-panel", TimelineWidget)
            timeline._stop_play()
            timeline._set_step(max(1, self.current_event_id - 1))
        except Exception:
            pass

    def action_step_next(self) -> None:
        """Move one step forward in the timeline."""
        try:
            timeline = self.query_one("#timeline-panel", TimelineWidget)
            timeline._stop_play()
            timeline._set_step(min(timeline.max_events, self.current_event_id + 1))
        except Exception:
            pass

    def action_toggle_play(self) -> None:
        """Toggle auto-play on the timeline."""
        try:
            timeline = self.query_one("#timeline-panel", TimelineWidget)
            if timeline._is_playing:
                timeline._stop_play()
            else:
                timeline._start_play()
        except Exception:
            pass

    def action_replay(self) -> None:
        """Jump back to step 1."""
        try:
            timeline = self.query_one("#timeline-panel", TimelineWidget)
            timeline._stop_play()
            timeline._set_step(1)
        except Exception:
            pass

    # ── Core refresh ─────────────────────────────────────────────────────────

    def refresh_ui(self) -> None:
        position = self.current_event_id
        line_to_highlight = 1
        historical_variables = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get line number for current step
                cursor.execute(
                    """
                    SELECT line_number
                    FROM events
                    ORDER BY id ASC
                    LIMIT 1 OFFSET ?
                    """,
                    (position - 1,),
                )
                row = cursor.fetchone()
                if row:
                    line_to_highlight = row[0]

                # Accumulate variable state up to current step
                cursor.execute(
                    """
                    SELECT variable_name, serialized_value
                    FROM events
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (position,),
                )
                for name, val in cursor.fetchall():
                    # Ignore internal variables
                    if name.startswith("__"):
                        continue
                    # Apply watchlist filter
                    if (
                        self.watched_variables is not None
                        and name not in self.watched_variables
                    ):
                        continue
                    historical_variables[name] = val

        except Exception:
            pass

        # Push updates to all display widgets
        try:
            self.query_one("#code-pane", CodeViewer).highlight_line(line_to_highlight)
            self.query_one("#var-inspector", VariablePanel).update_state(
                historical_variables
            )

            # Header step counter
            try:
                self.query_one("#header-step", Static).update(
                    f"⏱  Step {position} / {self._total_events}"
                )
            except Exception:
                pass

            # System status panel
            try:
                self.query_one("#status-panel", SystemStatusPanel).update_status(
                    event_count=self._total_events,
                    step=position,
                    total=self._total_events,
                )
            except Exception:
                pass

            self.sub_title = (
                f"Step {position}/{self._total_events}  ·  Line {line_to_highlight}"
            )

        except Exception:
            pass