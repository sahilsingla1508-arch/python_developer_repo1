import sqlite3

DATABASE = "chronicle.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def get_events():
    """
    Return all events ordered by execution.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,
               timestamp,
               line_number,
               variable_name,
               serialized_value
        FROM events
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_event_count():
    """
    Return total number of recorded events.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM events")

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_event(index: int):
    """
    Return the event at the given timeline index.
    """

    events = get_events()

    if not events:
        return None

    if index < 0 or index >= len(events):
        return None

    return events[index]
