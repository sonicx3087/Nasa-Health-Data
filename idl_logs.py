import os
import re
import sqlite3
from datetime import datetime

# Directory containing the log files
log_directory = r'/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_logs_idl'

# Pattern to match lines containing the word "FAILED"
failed_pattern = re.compile(r'FAILED', re.IGNORECASE)

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
cur = conn.cursor()

# Drop the existing log_entries_idl table if it exists

#cur.execute('DROP TABLE IF EXISTS log_entries_idl')

# Create the log_entries_idl table
cur.execute('''
CREATE TABLE log_entries_idl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_file TEXT NOT NULL,
    log_entry TEXT NOT NULL,
    entry_date TEXT NOT NULL
)
''')

# Function to parse log files and extract lines containing "FAILED"
def parse_log_files(directory):
    failed_messages = []

    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            # Extract the date from the filename (e.g., "vso_log_idl_20230110_070001.log")
            date_part = filename.split('_')[3]
            try:
                entry_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y-%m-%d')
            except ValueError:
                print(f"Filename {filename} contains an invalid date format.")
                continue

            with open(file_path, 'r') as file:
                for line in file:
                    if failed_pattern.search(line):
                        print(f"Match found in file {filename}: {line.strip()}")
                        failed_messages.append((filename, line.strip(), entry_date))

    return failed_messages

# Parse the log files and get the lines containing "FAILED"
failed_messages = parse_log_files(log_directory)

# Debugging: Print the extracted messages
print("Extracted messages:")
for log_file, log_entry, entry_date in failed_messages:
    print(f"{log_file}: {log_entry} (Date: {entry_date})")

# Insert the extracted messages into the log_entries_idl table
for log_file, log_entry, entry_date in failed_messages:
    cur.execute('''
        INSERT INTO log_entries_idl (log_file, log_entry, entry_date)
        VALUES (?, ?, ?)
    ''', (log_file, log_entry, entry_date))

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Log entries inserted successfully.")
