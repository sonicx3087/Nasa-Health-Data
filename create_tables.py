import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('check_files.db')
cursor = conn.cursor()

# Create the data_sources table
cursor.execute('''
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT UNIQUE
)
''')

# Create the status_records table
cursor.execute('''
CREATE TABLE IF NOT EXISTS status_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source_id INTEGER,
    status INTEGER,
    status_date DATE,
    FOREIGN KEY (data_source_id) REFERENCES data_sources (id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Tables created successfully.")
