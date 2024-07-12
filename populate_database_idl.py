#Imports
import os
import sqlite3
from datetime import datetime
import pandas as pd
import glob

# Directory containing the CSV files
directory = r'/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_checks_idl'



# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
cur = conn.cursor()




# Create the check_files_idl table with source_name
cur.execute('''
CREATE TABLE check_files_idl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    source TEXT NOT NULL,
    instrument TEXT NOT NULL,
    source_name TEXT NOT NULL,
    status INTEGER,
    check_date TEXT,
    UNIQUE (provider, source, instrument, check_date)
)
''')

# Function to insert data into check_files_idl table from a dataframe
def insert_check_file_data(df, check_date):
    for index, row in df.iterrows():
        source_name = f"{row['Provider']}-{row['Source']}-{row['Instrument']}"
        try:
            cur.execute('''
                INSERT INTO check_files_idl (provider, source, instrument, source_name, status, check_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['Provider'], row['Source'], row['Instrument'], source_name, row['Status'], check_date))
        except sqlite3.IntegrityError:
            print(f"Duplicate entry found for {row['Provider']}, {row['Source']}, {row['Instrument']}, {check_date}. Skipping.")
    conn.commit()

# Use glob to get all CSV files in the directory
path = os.path.join(directory, "*.csv")
for fname in glob.glob(path):
    print(fname)  # Full path to the CSV file
    # Extract information from the filename
    base = os.path.basename(fname)  # File name without directory path
    parts = base.split('_')  # Split the file name into components
    if len(parts) >= 4:
        # Ensure the date part is actually a date
        try:
            check_date_raw = parts[3]  # Extract the date part (YYYYMMDD format)
            # Convert the date part to YYYY-MM-DD format
            check_date = datetime.strptime(check_date_raw, '%Y%m%d').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Filename {base} contains an invalid date format.")
            continue

        # Load the CSV data into a DataFrame
        df = pd.read_csv(fname)

        # Insert data into the database
        insert_check_file_data(df, check_date)

# Close the connection
conn.close()