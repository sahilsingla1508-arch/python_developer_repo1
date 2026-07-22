"""
ui/app.py — PyChronicle UI ↔ data integration layer.

This module implements the integration adapter between the pipeline data layer
(SQLite events produced by pipeline/runner.py) and the UI presentation layer.

It provides:
  ChronicleDataAdapter  — fetches and filters stored execution events
  timeline_select()     — maps a timeline index → (source_line, variable_state)
  run_viewer()          — runs pipeline then prints an interactive timeline view

Design notes
------------
- Pure Python; no third-party UI framework required (textual/curses not assumed).
- Reads from the SQLite events table produced by pipeline/runner.run_pipeline().
- When Sahil's Textual UI is integrated, ChronicleDataAdapter supplies the
  data access methods; timeline_select supplies the index-to-state mapping.
- Source code display and variable panel content are returned as plain data
  (strings / dicts) so any UI layer can consume them.

Public API
----------
ChronicleDataAdapter(db_path)
    .get_events()                        -> list[dict]
    .get_events_at_line(line_no)         -> list[dict]
    .get_events_for_var(var_name)        -> list[dict]
    .get_distinct_lines()                -> list[int]
    .get_distinct_vars()                 -> list[str]

timeline_select(events, index, source_lines)
    -> {"event": dict, "source_line": str, "variable_state": dict}

run_viewer(script_path, db_path)
    -> runs pipeline then shows timeline output
"""

import os
import sqlite3
import sys

# ---------------------------------------------------------------------------
# Path helper: allow running as a script from the repo root
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from pipeline.runner import run_pipeline  # noqa: E402  (import after sys.path fixup)


# ---------------------------------------------------------------------------
# ChronicleDataAdapter
# ---------------------------------------------------------------------------

class ChronicleDataAdapter:
    """
    Read-only adapter over the SQLite events table created by pipeline/runner.

    Each event row is returned as a dict with keys:
        id, timestamp, line_number, variable_name, serialized_value
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _rows_to_dicts(self, rows) -> list:
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Public query methods
    # ------------------------------------------------------------------

    def get_events(self) -> list:
        """Return all events ordered by id (insertion order)."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, line_number, variable_name, serialized_value "
                "FROM events ORDER BY id"
            ).fetchall()
        return self._rows_to_dicts(rows)

    def get_events_at_line(self, line_no: int) -> list:
        """Return all events for a specific source line number."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, line_number, variable_name, serialized_value "
                "FROM events WHERE line_number = ? ORDER BY id",
                (line_no,),
            ).fetchall()
        return self._rows_to_dicts(rows)

    def get_events_for_var(self, var_name: str) -> list:
        """Return all events for a specific variable name."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, line_number, variable_name, serialized_value "
                "FROM events WHERE variable_name = ? ORDER BY id",
                (var_name,),
            ).fetchall()
        return self._rows_to_dicts(rows)

    def get_distinct_lines(self) -> list:
        """Return sorted list of distinct line numbers that have events."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT line_number FROM events ORDER BY line_number"
            ).fetchall()
        return [row[0] for row in rows]

    def get_distinct_vars(self) -> list:
        """Return sorted list of distinct variable names that have events."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT variable_name FROM events ORDER BY variable_name"
            ).fetchall()
        return [row[0] for row in rows]


# ---------------------------------------------------------------------------
# timeline_select — core integration function
# ---------------------------------------------------------------------------

def timeline_select(
    events: list,
    index: int,
    source_lines: list,
) -> dict:
    """
    Map a timeline index to the corresponding execution state.

    Given the full ordered list of trace events and a 0-based *index*,
    return a snapshot dict that the UI uses to update:
      - the code viewer (highlighted source line)
      - the variable panel (all variable values known up to this point)

    Parameters
    ----------
    events      : ordered list of event dicts (from ChronicleDataAdapter.get_events())
    index       : 0-based position in the event timeline
    source_lines: list of source-code strings (1-indexed via source_lines[lineno-1])

    Returns
    -------
    dict with keys:
        event          : the raw event dict at *index*
        source_line    : the source code text for the event's line_number (or "")
        variable_state : accumulated {var_name: value} for all events up to *index*
    """
    if not events:
        return {"event": None, "source_line": "", "variable_state": {}}

    # Clamp index to valid range
    index = max(0, min(index, len(events) - 1))
    event = events[index]

    # Accumulate variable state: replay all events up to and including index
    variable_state: dict = {}
    for ev in events[: index + 1]:
        variable_state[ev["variable_name"]] = ev["serialized_value"]

    # Retrieve the source line (1-indexed; guard against out-of-range)
    line_no = event["line_number"]
    if source_lines and 1 <= line_no <= len(source_lines):
        source_line = source_lines[line_no - 1]
    else:
        source_line = ""

    return {
        "event": event,
        "source_line": source_line,
        "variable_state": variable_state,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_source_lines(script_path: str) -> list:
    """Read script source and return list of lines (preserving content, no newlines)."""
    try:
        with open(script_path, "r", encoding="utf-8") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def _print_source_with_highlight(source_lines: list, highlight_line: int) -> None:
    """Print numbered source lines, marking the active line with >>>."""
    for i, line in enumerate(source_lines, start=1):
        marker = ">>>" if i == highlight_line else "   "
        print(f"  {marker} {i:3d} | {line}")


def _print_variable_panel(variable_state: dict) -> None:
    """Print the variable state panel."""
    if not variable_state:
        print("  (no variables captured yet)")
        return
    max_name_len = max(len(k) for k in variable_state)
    for name, value in sorted(variable_state.items()):
        print(f"  {name:<{max_name_len}} = {value}")


# ---------------------------------------------------------------------------
# run_viewer — end-to-end demo
# ---------------------------------------------------------------------------

def run_viewer(script_path: str, db_path: str = "chronicle.db") -> dict:
    """
    Run the PyChronicle pipeline on *script_path* then display an
    interactive-style timeline view in the terminal.

    Steps
    -----
    1. Execute the pipeline (AST + trace + SQLite).
    2. Load all events via ChronicleDataAdapter.
    3. For each event in the timeline, display:
         - the active source line (code viewer)
         - the accumulated variable state (variable panel)

    Returns the pipeline result dict.
    """
    print("=" * 60)
    print("PyChronicle — UI Data Integration View")
    print("=" * 60)
    print(f"Script : {script_path}")
    print(f"DB     : {db_path}")
    print()

    # 1. Run pipeline
    result = run_pipeline(script_path, db_path)

    if not result["success"]:
        print(f"[ERROR] Pipeline failed: {result['error']}")
        return result

    print(f"Pipeline OK — {result['event_count']} events captured")
    print(f"AST variables detected: {[v['variable_name'] for v in result['ast_variables']]}")
    print()

    # 2. Load events and source
    adapter = ChronicleDataAdapter(db_path)
    events = adapter.get_events()
    source_lines = _load_source_lines(script_path)

    if not events:
        print("No events to display.")
        return result

    # 3. Walk the timeline
    print(f"Timeline: {len(events)} events across lines "
          f"{adapter.get_distinct_lines()}")
    print()

    for idx in range(len(events)):
        state = timeline_select(events, idx, source_lines)
        ev = state["event"]

        print(f"--- Timeline event {idx + 1}/{len(events)} "
              f"(line {ev['line_number']}, "
              f"var={ev['variable_name']}, "
              f"val={ev['serialized_value']}) ---")

        # Code viewer
        print("[Code Viewer]")
        _print_source_with_highlight(source_lines, ev["line_number"])

        # Variable panel
        print("[Variable Panel]")
        _print_variable_panel(state["variable_state"])
        print()

    # Summary
    print("=" * 60)
    print(f"Timeline complete — {len(events)} events replayed")
    print(f"Distinct variables: {adapter.get_distinct_vars()}")
    print(f"Distinct lines    : {adapter.get_distinct_lines()}")
    print("=" * 60)

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ui/app.py <script.py> [db_path]")
        sys.exit(1)

    _script = sys.argv[1]
    _db = sys.argv[2] if len(sys.argv) > 2 else "chronicle.db"
    run_viewer(_script, _db)
