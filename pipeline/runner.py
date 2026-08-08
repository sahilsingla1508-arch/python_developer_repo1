"""
pipeline/runner.py — PyChronicle integration glue.

Entry point:
    run_pipeline(script_path, db_path="chronicle.db") -> dict

Wires together:
    1. AST analysis  (ast_parser.analyze)
    2. sys.settrace  (trace callback writing directly to SQLite)
    3. SQLite storage (events schema, insert, commit)

Design notes
------------
- Does NOT modify ast_parser.py, tracer.py, or storage.py.
- Manages its own SQLite connection so the pipeline is re-entrant
  (the module-level connection in tracer.py closes after one use;
   the pipeline needs to work for tests that call run_pipeline multiple times).
- Reuses the canonical events schema defined across the project:
      id, timestamp, line_number, variable_name, serialized_value
"""

import os
import sys
import sqlite3
from datetime import datetime

import ast_parser  # Prateek's module


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

_CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp        TEXT    NOT NULL,
    line_number      INTEGER NOT NULL,
    variable_name    TEXT    NOT NULL,
    serialized_value TEXT    NOT NULL
)
"""


def _init_db(db_path: str) -> sqlite3.Connection:
    """Open (or create) the SQLite database and ensure the events table exists."""
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_EVENTS)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Tracer callback factory
# ---------------------------------------------------------------------------

def _make_trace_callback(conn: sqlite3.Connection, script_path: str):
    """
    Return a sys.settrace-compatible callback that:
    - filters to frames belonging to *script_path* only
    - tracks variable deltas (only records changed values)
    - inserts each change as a row in the events table
    """
    cursor = conn.cursor()
    previous_values: dict = {}
    abs_script = os.path.abspath(script_path)

    def _trace(frame, event, arg):
        if event != "line":
            return _trace

        # Only trace frames from the target script
        frame_file = os.path.abspath(frame.f_code.co_filename)
        if frame_file != abs_script:
            return _trace

        line_no = frame.f_lineno
        local_vars = frame.f_locals.copy()

        for var_name, value in local_vars.items():
            # Skip Python internal/dunder variables
            if var_name.startswith("__"):
                continue

            # Skip built-in callables injected by exec
            if callable(value) and var_name in ("__builtins__",):
                continue

            key = var_name
            serialized = str(value)

            # Only record if value changed
            if previous_values.get(key) == serialized:
                continue

            previous_values[key] = serialized
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO events (timestamp, line_number, variable_name, serialized_value) "
                "VALUES (?, ?, ?, ?)",
                (timestamp, line_no, var_name, serialized),
            )

        return _trace

    return _trace


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_pipeline(script_path: str, db_path: str = "chronicle.db") -> dict:
    """
    Execute the full PyChronicle pipeline for *script_path*.

    Steps
    -----
    1. Validate the script path.
    2. Run AST analysis to collect static variable metadata.
    3. Initialise (or open) the SQLite database.
    4. Execute the script under sys.settrace, persisting every variable
       change as an event row.
    5. Commit, close, and return a summary dictionary.

    Parameters
    ----------
    script_path : str
        Path to the Python script to analyse and trace.
    db_path : str
        Path to the SQLite database file (created if absent).

    Returns
    -------
    dict with keys:
        success        : bool
        script_path    : str
        db_path        : str
        ast_variables  : list[dict]   — static AST output
        event_count    : int          — rows written to events table
        error          : str | None
    """
    script_path = os.path.abspath(script_path)

    if not os.path.isfile(script_path):
        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": [],
            "event_count": 0,
            "error": f"Script not found: {script_path}",
        }

    # 1. AST analysis
    try:
        ast_variables = ast_parser.analyze(script_path)
    except Exception as exc:
        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": [],
            "event_count": 0,
            "error": f"AST analysis failed: {exc}",
        }

    # 2. Read source
    with open(script_path, "r", encoding="utf-8") as fh:
        source = fh.read()

    # 3. Init DB
    conn = _init_db(db_path)

    # 4. Execute under tracer
    trace_cb = _make_trace_callback(conn, script_path)
    exec_namespace: dict = {}
    error_msg = None

    sys.settrace(trace_cb)
    try:
        compiled = compile(source, script_path, "exec")
        exec(compiled, exec_namespace, exec_namespace)  # noqa: S102
    except Exception as exc:
        error_msg = str(exc)
    finally:
        sys.settrace(None)
        conn.commit()

    # 5. Count persisted events
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    conn.close()

    return {
        "success": error_msg is None,
        "script_path": script_path,
        "db_path": db_path,
        "ast_variables": ast_variables,
        "event_count": event_count,
        "error": error_msg,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.runner <script.py> [db_path]")
        sys.exit(1)

    _script = sys.argv[1]
    _db = sys.argv[2] if len(sys.argv) > 2 else "chronicle.db"

    result = run_pipeline(_script, _db)

    print("=" * 50)
    print("PyChronicle Pipeline Result")
    print("=" * 50)
    print(f"Success     : {result['success']}")
    print(f"Script      : {result['script_path']}")
    print(f"DB          : {result['db_path']}")
    print(f"AST vars    : {json.dumps(result['ast_variables'], indent=2)}")
    print(f"Event count : {result['event_count']}")
    if result["error"]:
        print(f"Error       : {result['error']}")
    print("=" * 50)
