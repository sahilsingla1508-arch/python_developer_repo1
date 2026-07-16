import sys
import sqlite3
from datetime import datetime

def get_connection():
    conn = sqlite3.connect("chronicle.db")
    return conn

def trace_lines(frame, event, arg):
    if event == "line":
        line_no = frame.f_lineno
        local_vars = frame.f_locals.copy()

        conn = get_connection()
        cursor = conn.cursor()

        for var_name, value in local_vars.items():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serialized_value = str(value)

            cursor.execute("""
                INSERT INTO events (timestamp, line_number, variable_name, serialized_value)
                VALUES (?, ?, ?, ?)
            """, (timestamp, line_no, var_name, serialized_value))

        conn.commit()
        conn.close()

    return trace_lines

def run_with_trace(filename):
    with open(filename, "r") as f:
        code = f.read()
    sys.settrace(trace_lines)
    exec(compile(code, filename, "exec"))
    sys.settrace(None)

if __name__ == "__main__":
    run_with_trace("sample2.py")
