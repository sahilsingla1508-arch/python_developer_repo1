import json
from storage import get_connection, get_events


def export_json(db_path, output_file):
    with get_connection(db_path) as conn:
        events = get_events(conn)

    data = []

    for row in events:
        data.append({
            "id": row[0],
            "timestamp": row[1],
            "step": row[2],
            "line": row[3],
            "variable": row[4],
            "value": row[5],
        })

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)