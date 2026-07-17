import sqlite3

# Connect to (and create) the database file
conn = sqlite3.connect("chronicle.db")
cursor = conn.cursor()

# Create the table with the required columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    serialized_value TEXT NOT NULL
)
""")

# Insert a test row
cursor.execute("""
INSERT INTO events (timestamp, line_number, variable_name, serialized_value)
VALUES (?, ?, ?, ?)
""", ("2026-07-11 10:00:00", 1, "name", "Tejas"))

# Save changes
conn.commit()

# Read back and print all rows to confirm it worked
cursor.execute("SELECT * FROM events")
rows = cursor.fetchall()
print("Current data in the table:")
for row in rows:
    print(row)

conn.close()
print("Database created and tested successfully!")