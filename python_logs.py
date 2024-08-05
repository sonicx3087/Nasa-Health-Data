import os
import re
import sqlite3
from datetime import datetime

# Directory containing the log files
log_directory = r'/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_logs_python'

# Pattern to match lines containing the word "FAILED" or warning messages
error_warning_pattern = re.compile(r'(FAILED|WARNING|ERROR).*', re.IGNORECASE)
source_name_pattern = re.compile(r'(\w+) \| (\w+) \| (\w+)', re.IGNORECASE)

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
cur = conn.cursor()

# Drop the existing log_entries_python table if it exists
#cur.execute('DROP TABLE IF EXISTS log_entries_python')

# Create the log_entries_python table with source_name
cur.execute('''
CREATE TABLE log_entries_python (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_file TEXT NOT NULL,
    log_entry TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    source_name TEXT,
    error_message TEXT
)
''')

# Function to parse log files and extract lines containing errors/warnings and source_name
def parse_log_files(directory):
    failed_messages = []

    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            date_part = filename.split('_')[2]
            try:
                entry_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y-%m-%d')
            except ValueError:
                print(f"Filename {filename} contains an invalid date format.")
                continue

            with open(file_path, 'r') as file:
                for line in file:
                    if error_warning_pattern.search(line):
                        source_match = source_name_pattern.search(line)
                        if source_match:
                            provider, source, instrument = source_match.groups()
                            source_name = f"{provider}-{source}-{instrument}"
                            error_message = line.strip()
                            failed_messages.append((filename, line.strip(), entry_date, source_name, error_message))

    return failed_messages

# Parse the log files and get the lines containing errors/warnings
failed_messages = parse_log_files(log_directory)

# Insert the extracted messages into the log_entries_python table
for log_file, log_entry, entry_date, source_name, error_message in failed_messages:
    cur.execute('''
        INSERT INTO log_entries_python (log_file, log_entry, entry_date, source_name, error_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (log_file, log_entry, entry_date, source_name, error_message))

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Log entries inserted successfully.")

