import sqlite3
from contextlib import contextmanager


def init_db(db_path: str = "chronicle.db"):
    """
    Creates the events table if it does not exist.

    Also upgrades an older events table if step_number
    is missing.
    """

    conn = sqlite3.connect(db_path)

    # Create the table for a new database
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            step_number INTEGER NOT NULL DEFAULT 0,
            line_number INTEGER NOT NULL,
            variable_name TEXT NOT NULL,
            serialized_value TEXT NOT NULL
        )
    """)

    # Check the existing table structure
    columns = conn.execute(
        "PRAGMA table_info(events)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    # Upgrade an old database that doesn't have step_number
    if "step_number" not in column_names:
        conn.execute("""
            ALTER TABLE events
            ADD COLUMN step_number INTEGER NOT NULL DEFAULT 0
        """)

    conn.commit()

    return conn


@contextmanager
def get_connection(db_path: str = "chronicle.db"):
    """
    Opens a database connection and closes it automatically.
    """

    conn = sqlite3.connect(db_path)

    try:
        yield conn
    finally:
        conn.close()


def insert_event(
    conn,
    timestamp,
    step_number,
    line_number,
    variable_name,
    serialized_value
):
    """
    Inserts one variable-change event into the database.
    """

    conn.execute(
        """
        INSERT INTO events (
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value,
        ),
    )


def get_events(conn):
    """
    Returns all recorded events in execution order.
    """

    return conn.execute(
        """
        SELECT
            id,
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value
        FROM events
        ORDER BY id
        """
    ).fetchall()


def get_event_by_step(conn, step_number):
    """
    Returns all variable updates that occurred
    at a particular execution step.
    """

    return conn.execute(
        """
        SELECT
            id,
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value
        FROM events
        WHERE step_number = ?
        ORDER BY id
        """,
        (step_number,),
    ).fetchall()


def get_variable_history(conn, variable_name):
    """
    Returns every recorded change for a specific variable.
    """

    return conn.execute(
        """
        SELECT
            id,
            timestamp,
            step_number,
            line_number,
            variable_name,
            serialized_value
        FROM events
        WHERE variable_name = ?
        ORDER BY step_number
        """,
        (variable_name,),
    ).fetchall()


def get_total_steps(conn):
    """
    Returns the total number of execution steps.
    """

    result = conn.execute(
        """
        SELECT MAX(step_number)
        FROM events
        """
    ).fetchone()

    return result[0] if result[0] else 0


def get_trace_statistics(conn):
    """
    Returns basic statistics about the trace.
    """

    total_events = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    unique_variables = conn.execute(
        """
        SELECT COUNT(DISTINCT variable_name)
        FROM events
        """
    ).fetchone()[0]

    total_steps = conn.execute(
        """
        SELECT MAX(step_number)
        FROM events
        """
    ).fetchone()[0]

    return {
        "events": total_events,
        "variables": unique_variables,
        "steps": total_steps or 0,
    }


def clear_events(conn):
    """
    Deletes all recorded trace events.
    """

    conn.execute("DELETE FROM events")
    conn.commit()


if __name__ == "__main__":
    # Manual test
    conn = init_db()

    insert_event(
        conn,
        "2026-07-22 10:00:00",
        1,
        1,
        "test",
        "123",
    )

    conn.commit()

    print("All Events")
    print(get_events(conn))

    print()

    print("Variable History")
    print(get_variable_history(conn, "test"))

    print()

    print("Total Steps")
    print(get_total_steps(conn))

    print()

    print("Trace Statistics")
    print(get_trace_statistics(conn))

    conn.close()