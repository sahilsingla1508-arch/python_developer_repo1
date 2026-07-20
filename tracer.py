import sys
import sqlite3
from datetime import datetime

# Keep track of previous values (Delta Tracking)
previous_values = {}

# Open database connection once
conn = sqlite3.connect("chronicle.db")
cursor = conn.cursor()


def trace_lines(frame, event, arg):
    if event == "line":

        line_no = frame.f_lineno
        local_vars = frame.f_locals.copy()

        for var_name, value in local_vars.items():

            # Skip Python internal variables
            if var_name.startswith("__"):
                continue

            # Store only if value changed
            if previous_values.get(var_name) == value:
                continue

            previous_values[var_name] = value

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serialized_value = str(value)

            cursor.execute("""
                INSERT INTO events
                (timestamp, line_number, variable_name, serialized_value)
                VALUES (?, ?, ?, ?)
            """, (timestamp, line_no, var_name, serialized_value))

            print(f"Line {line_no}: {var_name} = {value}")

    return trace_lines


def run_with_trace(filename):

    # Clear old trace
    cursor.execute("DELETE FROM events")
    conn.commit()

    with open(filename, "r") as f:
        code = f.read()

    trace_namespace = {}

    sys.settrace(trace_lines)

    try:
        exec(compile(code, filename, "exec"), trace_namespace)

    except Exception as e:
        print(f"Execution Error: {e}")

    finally:
        sys.settrace(None)
        conn.commit()

        # Display total number of trace events
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        print(f"Total events recorded: {count}")

        conn.close()


if __name__ == "__main__":
    run_with_trace("sample2.py")
