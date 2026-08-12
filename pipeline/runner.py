"""
pipeline/runner.py — PyChronicle integration glue.

Pipeline:
1. AST analysis
2. Execute Python script with sys.settrace
3. Track variable mutations
4. Capture print() output
5. Store events in SQLite
6. Provide timeline data to the UI
"""

import os
import sys
import sqlite3
import builtins
from datetime import datetime

import ast_parser

from storage import (
    init_db,
    clear_events,
    insert_event,
)


# ---------------------------------------------------------------------------
# Trace callback
# ---------------------------------------------------------------------------

def _make_trace_callback(
    conn: sqlite3.Connection,
    script_path: str,
    state: dict,
):
    """
    Creates the sys.settrace callback.

    Python's line trace event happens BEFORE the line executes.
    Therefore, a variable mutation detected at the next line belongs
    to the previous line.
    """

    previous_values = {}

    abs_script = os.path.abspath(script_path)

    def _trace(frame, event, arg):

        if event != "line":
            return _trace

        # ---------------------------------------------------------------
        # Only trace the target script
        # ---------------------------------------------------------------

        frame_file = os.path.abspath(
            frame.f_code.co_filename
        )

        if frame_file != abs_script:
            return _trace

        # ---------------------------------------------------------------
        # Current line
        # ---------------------------------------------------------------

        current_line = frame.f_lineno

        local_vars = frame.f_locals.copy()

        # ---------------------------------------------------------------
        # Determine mutation line
        # ---------------------------------------------------------------

        previous_line = state["previous_line"]

        if previous_line is None:
            line_to_record = current_line
        else:
            line_to_record = previous_line

        # ---------------------------------------------------------------
        # Check variables
        # ---------------------------------------------------------------

        for var_name, value in local_vars.items():

            # Ignore Python internal variables
            if var_name.startswith("__"):
                continue

            serialized = str(value)

            # Ignore unchanged variables
            if (
                var_name in previous_values
                and previous_values[var_name] == serialized
            ):
                continue

            # Store latest value
            previous_values[var_name] = serialized

            # Increment mutation step
            state["step_counter"] += 1

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Save mutation
            insert_event(
                conn,
                timestamp,
                state["step_counter"],
                line_to_record,
                var_name,
                serialized,
            )

        # Current line becomes previous line
        state["previous_line"] = current_line

        return _trace

    return _trace


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    script_path: str,
    db_path: str = "chronicle.db",
) -> dict:
    """
    Execute the complete PyChronicle pipeline.

    Every execution starts with a clean event history.
    """

    # -------------------------------------------------------------------
    # 1. Absolute script path
    # -------------------------------------------------------------------

    script_path = os.path.abspath(script_path)

    # -------------------------------------------------------------------
    # 2. Validate script
    # -------------------------------------------------------------------

    if not os.path.isfile(script_path):

        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": [],
            "event_count": 0,
            "error": f"Script not found: {script_path}",
        }

    # -------------------------------------------------------------------
    # 3. AST analysis
    # -------------------------------------------------------------------

    try:

        ast_variables = ast_parser.analyze(
            script_path
        )

    except Exception as exc:

        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": [],
            "event_count": 0,
            "error": f"AST analysis failed: {exc}",
        }

    # -------------------------------------------------------------------
    # 4. Read source
    # -------------------------------------------------------------------

    try:

        with open(
            script_path,
            "r",
            encoding="utf-8",
        ) as file:

            source = file.read()

    except Exception as exc:

        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": ast_variables,
            "event_count": 0,
            "error": f"Unable to read script: {exc}",
        }

    conn = None

    try:

        # ---------------------------------------------------------------
        # 5. Initialize database
        # ---------------------------------------------------------------

        conn = init_db(db_path)

        # Remove previous execution
        clear_events(conn)

        print(
            f"[PyChronicle] Tracing "
            f"{os.path.basename(script_path)}..."
        )

        # ---------------------------------------------------------------
        # 6. State used by tracer
        # ---------------------------------------------------------------

        state = {
            "previous_line": None,
            "step_counter": 0,
        }

        # ---------------------------------------------------------------
        # 7. Capture program output
        # ---------------------------------------------------------------

        captured_output = []

        original_print = builtins.print

        def captured_print(*args, **kwargs):
            """
            Replacement for print() used by the target script.

            It:
            1. Captures the output for PyChronicle.
            2. Still prints normally to the terminal.
            """

            output_text = " ".join(
                str(arg)
                for arg in args
            )

            captured_output.append(
                output_text
            )

            # Still show output in terminal
            original_print(
                *args,
                **kwargs
            )

        # ---------------------------------------------------------------
        # 8. Create trace callback
        # ---------------------------------------------------------------

        trace_callback = _make_trace_callback(
            conn,
            script_path,
            state,
        )

        # ---------------------------------------------------------------
        # 9. Execution namespace
        # ---------------------------------------------------------------

        exec_namespace = {
            "__name__": "__main__",
            "__file__": script_path,

            # This makes print() use our capture function
            "print": captured_print,
        }

        error_msg = None

        # ---------------------------------------------------------------
        # 10. Execute target script
        # ---------------------------------------------------------------

        sys.settrace(trace_callback)

        try:

            compiled = compile(
                source,
                script_path,
                "exec",
            )

            exec(
                compiled,
                exec_namespace,
                exec_namespace,
            )

        except Exception as exc:

            error_msg = str(exc)

        finally:

            # Disable tracing
            sys.settrace(None)

        # ---------------------------------------------------------------
        # 11. Restore normal print
        # ---------------------------------------------------------------

        builtins.print = original_print

        # ---------------------------------------------------------------
        # 12. Save captured output
        # ---------------------------------------------------------------

        if captured_output:

            output_text = "\n".join(
                captured_output
            )

            state["step_counter"] += 1

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # The print() statement is the final line
            # of sample2.py.
            final_line = len(
                source.splitlines()
            )

            insert_event(
                conn,
                timestamp,
                state["step_counter"],
                final_line,
                "__output__",
                output_text,
            )

        # ---------------------------------------------------------------
        # 13. If there was no output, add script-end marker
        # ---------------------------------------------------------------

        elif state["previous_line"] is not None:

            state["step_counter"] += 1

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            insert_event(
                conn,
                timestamp,
                state["step_counter"],
                state["previous_line"],
                "__script_end__",
                "completed",
            )

        # ---------------------------------------------------------------
        # 14. Commit
        # ---------------------------------------------------------------

        conn.commit()

        # ---------------------------------------------------------------
        # 15. Count events
        # ---------------------------------------------------------------

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM events"
        )

        event_count = cursor.fetchone()[0]

        # ---------------------------------------------------------------
        # 16. Close database
        # ---------------------------------------------------------------

        conn.close()
        conn = None

        # ---------------------------------------------------------------
        # 17. Return result
        # ---------------------------------------------------------------

        return {
            "success": error_msg is None,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": ast_variables,
            "event_count": event_count,
            "error": error_msg,
        }

    except Exception as exc:

        # Make sure tracing is disabled
        sys.settrace(None)

        # Restore print
        try:
            builtins.print = original_print
        except Exception:
            pass

        if conn is not None:

            try:
                conn.close()
            except Exception:
                pass

        return {
            "success": False,
            "script_path": script_path,
            "db_path": db_path,
            "ast_variables": ast_variables,
            "event_count": 0,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    import json

    if len(sys.argv) < 2:

        print(
            "Usage: python -m pipeline.runner "
            "<script.py> [db_path]"
        )

        sys.exit(1)

    script = sys.argv[1]

    if len(sys.argv) > 2:
        db = sys.argv[2]
    else:
        db = "chronicle.db"

    result = run_pipeline(
        script,
        db,
    )

    print("=" * 50)
    print("PyChronicle Pipeline Result")
    print("=" * 50)

    print(
        f"Success     : {result['success']}"
    )

    print(
        f"Script      : {result['script_path']}"
    )

    print(
        f"DB          : {result['db_path']}"
    )

    print(
        "AST vars    : "
        + json.dumps(
            result["ast_variables"],
            indent=2,
        )
    )

    print(
        f"Event count : {result['event_count']}"
    )

    if result["error"]:

        print(
            f"Error       : {result['error']}"
        )

    print("=" * 50)