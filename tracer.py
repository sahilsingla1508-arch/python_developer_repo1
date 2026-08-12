import sys
import copy
import json
from datetime import datetime

from storage import insert_event


def make_tracer(conn, state=None):
    """
    Returns a trace function bound to a specific DB connection.

    `state` is used to expose:
    - last executed line
    - current step counter
    """

    if state is None:
        state = {}

    prev_values = {}
    last_line = {"value": None}
    step_counter = {"value": 0}

    # Expose tracing state to run_with_trace()
    state["last_line"] = last_line
    state["step_counter"] = step_counter

    def trace_lines(frame, event, arg):
        if event == "line":
            current_line = frame.f_lineno
            local_vars = frame.f_locals.copy()

            # DEBUG: show traced line and current variables
            print("TRACE:", current_line, local_vars)

            for var_name, value in local_vars.items():

                # Ignore Python internal variables
                if var_name.startswith("__"):
                    continue

                # Make a safe snapshot of the value
                snapshot = (
                    copy.deepcopy(value)
                    if _is_deepcopyable(value)
                    else value
                )

                # If variable value has not changed, don't create
                # another history event
                if (
                    var_name in prev_values
                    and prev_values[var_name] == snapshot
                ):
                    continue

                # Store latest value
                prev_values[var_name] = snapshot

                # Associate mutation with the previous line when possible
                line_to_record = (
                    last_line["value"]
                    if last_line["value"] is not None
                    else current_line
                )

                # Increment debugger step
                step_counter["value"] += 1

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Save variable mutation to database
                insert_event(
                    conn,
                    timestamp,
                    step_counter["value"],
                    line_to_record,
                    var_name,
                    serialize_value(value),
                )

            # Update last executed line
            last_line["value"] = current_line

        return trace_lines

    return trace_lines


def serialize_value(value):
    """
    Convert a value to a string for storage.

    JSON is preferred for cleaner structured values.
    Falls back to str() when JSON serialization is not possible.
    """

    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return str(value)


def _is_deepcopyable(value):
    """
    Check whether a value can safely be deep-copied.
    """

    try:
        copy.deepcopy(value)
        return True
    except Exception:
        return False


def run_with_trace(filename: str, conn):
    """
    Runs a Python script under tracing and writes
    variable changes to the database.
    """

    # Read source code
    with open(filename, "r") as f:
        code = f.read()

    # Create tracing state
    state = {}

    # Create tracer
    tracer = make_tracer(conn, state)

    # Enable tracing
    sys.settrace(tracer)

    try:
        # Execute the target Python file
        exec(compile(code, filename, "exec"), {})

    finally:
        # Always disable tracing
        sys.settrace(None)

    # The final line, such as print(), may not mutate a variable.
    # Add a completion marker so the debugger timeline can reach it.
    last_line_seen = state.get("last_line", {}).get("value")

    if last_line_seen is not None:

        step_counter = state.setdefault(
            "step_counter",
            {"value": 0}
        )

        step_counter["value"] += 1

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        insert_event(
            conn,
            timestamp,
            step_counter["value"],
            last_line_seen,
            "__script_end__",
            "completed",
        )

    # Save all events
    conn.commit()


if __name__ == "__main__":
    from storage import init_db

    conn = init_db()

    run_with_trace("sample2.py", conn)

    conn.close()