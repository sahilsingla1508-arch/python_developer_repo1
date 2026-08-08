import sys
import copy
from datetime import datetime
from storage import insert_event


def make_tracer(conn, state=None):
    """Returns a trace function bound to a specific DB connection.
    `state` (if given) will be updated with the last line seen, so the
    caller can read it after tracing finishes."""
    if state is None:
        state = {}
    prev_values = {}
    last_line = {"value": None}
    state["last_line"] = last_line  # expose so run_with_trace can read it later

    def trace_lines(frame, event, arg):
        if event == "line":
            current_line = frame.f_lineno
            local_vars = frame.f_locals.copy()

            for var_name, value in local_vars.items():
                if var_name.startswith("__"):
                    continue

                snapshot = copy.deepcopy(value) if _is_deepcopyable(value) else value

                if var_name in prev_values and prev_values[var_name] == snapshot:
                    continue

                prev_values[var_name] = snapshot

                line_to_record = (
                    last_line["value"] if last_line["value"] is not None else current_line
                )

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_event(conn, timestamp, line_to_record, var_name, str(value))

            last_line["value"] = current_line

        return trace_lines

    return trace_lines


def _is_deepcopyable(value):
    try:
        copy.deepcopy(value)
        return True
    except Exception:
        return False


def run_with_trace(filename: str, conn):
    """Runs a script under trace, writing every variable change to conn."""
    with open(filename, "r") as f:
        code = f.read()

    state = {}
    tracer = make_tracer(conn, state)

    sys.settrace(tracer)
    try:
        exec(compile(code, filename, "exec"), {})
    finally:
        sys.settrace(None)

    # The final line (e.g. a print statement) often doesn't mutate any
    # variable, so it never gets its own event. Insert a completion
    # marker so the timeline can reach it.
    last_line_seen = state.get("last_line", {}).get("value")
    if last_line_seen is not None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_event(conn, timestamp, last_line_seen, "__script_end__", "completed")


if __name__ == "__main__":
    from storage import init_db
    conn = init_db()
    run_with_trace("sample_2.py", conn)
    conn.close()
