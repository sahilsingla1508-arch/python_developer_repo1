import sqlite3
from contextlib import contextmanager


def init_db(db_path: str = "chronicle.db"):
    """Creates the events table if it doesn't exist. Returns a connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            variable_name TEXT NOT NULL,
            serialized_value TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


@contextmanager
def get_connection(db_path: str = "chronicle.db"):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def insert_event(conn, timestamp, step_number, line_number, variable_name, serialized_value):
    conn.execute(
        "INSERT INTO events (timestamp, step_number, line_number, variable_name, serialized_value) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value,
        ),
    )


def get_events(conn):
    return conn.execute("SELECT * FROM events ORDER BY id").fetchall()


def get_event_by_step(conn, step_number):
    """
    Returns all variable updates that occurred
    at a particular execution step.
    """
    return conn.execute(
        """
        SELECT *
        FROM events
        WHERE step_number = ?
        """,
        (step_number,),
    ).fetchall()


def get_variable_history(conn, variable_name):
    """
    Returns every change recorded
    for a specific variable.
    """
    return conn.execute(
        """
        SELECT *
        FROM events
        WHERE variable_name = ?
        ORDER BY step_number
        """,
        (variable_name,),
    ).fetchall()


def get_total_steps(conn):
    """
    Returns total execution steps.
    """

    result = conn.execute(
        """
        SELECT MAX(step_number)
        FROM events
        """
    ).fetchone()

    return result[0] if result[0] else 0


def clear_events(conn):
    conn.execute("DELETE FROM events")
    conn.commit()


if __name__ == "__main__":
    # Manual test — only runs when you execute this file directly
    conn = init_db()
    insert_event(conn, "2026-07-22 10:00:00", 1, 1, "test", "123")

    print("All Events")
    print(get_events(conn))

    print()

    print("Variable History")
    print(get_variable_history(conn, "test"))

    print()

    print("Total Steps")
    print(get_total_steps(conn))

    conn.close()