import pandas as pd
import sqlite3
from datetime import datetime
import os

# Directory containing the CSV files
directory = os.path.expanduser('~/Downloads/vso_health_checks_python')

# Connect to the SQLite database
conn = sqlite3.connect('check_files.db')
cursor = conn.cursor()

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.startswith('vso_health_checks_') and filename.endswith('.csv'):
        file_path = os.path.join(directory, filename)

        # Read the CSV file using pandas
        df = pd.read_csv(file_path)

        # Iterate over the DataFrame rows
        for index, row in df.iterrows():
            provider = row['Provider']
            source = row['Source']
            instrument = row['Instrument']
            status = int(row['Status'])
            status_date = datetime.now().strftime('%Y-%m-%d')  # or use a specific date if available

            source_name = f"{provider}-{source}-{instrument}"

            # Insert into data_sources table
            cursor.execute("INSERT OR IGNORE INTO data_sources (source_name) VALUES (?)", (source_name,))
            cursor.execute("SELECT id FROM data_sources WHERE source_name = ?", (source_name,))
            data_source_id = cursor.fetchone()[0]

            # Insert into status_records table
            cursor.execute("INSERT INTO status_records (data_source_id, status, status_date) VALUES (?, ?, ?)",
                           (data_source_id, status, status_date))

# Commit the transaction
conn.commit()
conn.close()
