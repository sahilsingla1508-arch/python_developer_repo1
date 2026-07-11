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

# Save changes
conn.commit()
conn.close()

print("Database and schema created successfully!")