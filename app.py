import sqlite3

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, SelectionList
from textual_slider import Slider
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

# Import custom modular widgets
from code_viewer import CodeViewer
from variable_panel import VariablePanel
from timeline import TimelineWidget
from watchlist_panel import WatchlistPanel


class PyChronicleUI(App):
    """
    Core UI Application Orchestrator linking the layout windows.
    """

    CSS_PATH = "styles.tcss"

    # Press Q to quit
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    current_event_id = reactive(1)

    def __init__(
        self,
        target_script: str,
        db_path: str = "chronicle.db",
        **kwargs
    ):
        super().__init__(**kwargs)

        self.target_script = target_script
        self.db_path = db_path

        # None means watchlist has not been initialized yet.
        self.watched_variables = None

    def compose(self) -> ComposeResult:

        yield Header(show_clock=True)

        with Horizontal(id="workspace"):

            # ---------------------------------------------------------
            # Code Viewer
            # ---------------------------------------------------------

            with Vertical(id="code-container"):

                yield Static(
                    f"💻 LIVE RUN ARCHITECTURE: {self.target_script}",
                    classes="pane-title"
                )

                yield CodeViewer(
                    file_path=self.target_script,
                    id="code-pane"
                )

            # ---------------------------------------------------------
            # Variable Inspector + Watchlist
            # ---------------------------------------------------------

            with Vertical(id="inspector-container"):

                yield Static(
                    "🔍 DELTA VARIABLE HISTORY TRACKER",
                    classes="pane-title"
                )

                yield VariablePanel(
                    id="var-inspector"
                )

                yield Static(
                    "👁 WATCH VARIABLES",
                    classes="pane-title"
                )

                yield WatchlistPanel(
                    target_script=self.target_script,
                    id="watchlist"
                )

        # -------------------------------------------------------------
        # Timeline
        # -------------------------------------------------------------

        yield TimelineWidget(
            db_path=self.db_path,
            id="timeline-panel"
        )

        yield Footer()

    def on_mount(self) -> None:

        self.title = "PyChronicle Debugger"

        # Initially select all variables
        try:

            watchlist = self.query_one(
                "#watchlist",
                WatchlistPanel
            )

            self.watched_variables = set(
                watchlist.get_selected_variables()
            )

        except Exception:

            self.watched_variables = set()

        self.refresh_ui()

    def on_selection_list_selection_toggled(
        self,
        event: SelectionList.SelectionToggled
    ) -> None:
        """
        Called whenever a variable is checked/unchecked
        in the Watchlist.
        """

        if event.selection_list.id != "watchlist":
            return

        watchlist = self.query_one(
            "#watchlist",
            WatchlistPanel
        )

        self.watched_variables = set(
            watchlist.get_selected_variables()
        )

        self.refresh_ui()

    def on_slider_changed(
        self,
        event: Slider.Changed
    ) -> None:

        self.current_event_id = int(event.value)

    def watch_current_event_id(
        self,
        new_id: int
    ) -> None:

        self.refresh_ui()

    def refresh_ui(self):

        position = self.current_event_id

        line_to_highlight = 1

        historical_variables = {}

        try:

            with sqlite3.connect(self.db_path) as conn:

                cursor = conn.cursor()

                # -----------------------------------------------------
                # Get selected event's line number
                # -----------------------------------------------------

                cursor.execute(
                    """
                    SELECT line_number
                    FROM events
                    ORDER BY id ASC
                    LIMIT 1 OFFSET ?
                    """,
                    (position - 1,)
                )

                row = cursor.fetchone()

                if row:

                    line_to_highlight = row[0]

                # -----------------------------------------------------
                # Get all events up to selected timeline position
                # -----------------------------------------------------

                cursor.execute(
                    """
                    SELECT
                        variable_name,
                        serialized_value
                    FROM events
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (position,)
                )

                rows = cursor.fetchall()

                for name, val in rows:

                    # -------------------------------------------------
                    # Output event
                    # -------------------------------------------------

                    if name == "__output__":

                        historical_variables["Output"] = val
                        continue

                    # -------------------------------------------------
                    # Ignore internal variables
                    # -------------------------------------------------

                    if name.startswith("__"):

                        continue

                    # -------------------------------------------------
                    # Apply Watchlist filter
                    # -------------------------------------------------

                    if (
                        self.watched_variables is not None
                        and name not in self.watched_variables
                    ):
                        continue

                    # -------------------------------------------------
                    # Store latest variable value
                    # -------------------------------------------------

                    historical_variables[name] = val

        except Exception as e:

            print(
                f"Error refreshing UI: {e}"
            )

        # -------------------------------------------------------------
        # Update Code Viewer and Variable Panel
        # -------------------------------------------------------------

        try:

            self.query_one(
                "#code-pane",
                CodeViewer
            ).highlight_line(
                line_to_highlight
            )

            self.query_one(
                "#var-inspector",
                VariablePanel
            ).update_state(
                historical_variables
            )

            self.sub_title = (
                f"Step Mutation: {position} | "
                f"Highlighted Line: {line_to_highlight}"
            )

        except Exception as e:

            print(
                f"Error updating UI: {e}"
            )