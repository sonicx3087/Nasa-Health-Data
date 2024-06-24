import os
import sqlite3
from datetime import datetime
import pandas as pd

# Directory containing the CSV files
directory = r'/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_checks_python'

# Connect to the SQLite database
conn = sqlite3.connect('check_files.db')
cur = conn.cursor()

# Create the check_files table
cur.execute('''
CREATE TABLE IF NOT EXISTS check_files_python (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    source TEXT,
    instrument TEXT,
    status INTEGER,
    check_date DATE
)
''')

# Function to insert data into the check_files table from a dataframe
def insert_check_file_data(df, check_date):
    for index, row in df.iterrows():
        cur.execute('''
            INSERT INTO check_files_python (provider, source, instrument, status, check_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['Provider'], row['Source'], row['Instrument'], row['Status'], check_date))
    conn.commit()

# Iterate through all CSV files in the directory and insert their data into the database
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory, filename)
        try:
            df = pd.read_csv(file_path)
            print(f"CSV file loaded successfully: {filename}")
            # Extract date from the filename (assuming the format is consistent)
            date_str = filename.split('_')[3][:8]  # Extract the date part
            check_date = datetime.strptime(date_str, '%Y%m%d').date()
            insert_check_file_data(df, check_date)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while loading the file {filename}: {e}")

# Close the database connection
conn.close()
print("Data inserted successfully.")