import os
import re
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save, show
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool
from bokeh.palettes import Spectral6
from html2image import Html2Image

# Directory containing the log files
log_directory = r'/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_logs_idl'

# Pattern to match lines containing the word "FAILED"
failed_pattern = re.compile(r'FAILED', re.IGNORECASE)

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
cur = conn.cursor()

# Create or replace the log_entries_idl table if needed
cur.execute('''
CREATE TABLE IF NOT EXISTS log_entries_idl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_file TEXT NOT NULL,
    log_entry TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    source_name TEXT,
    message TEXT
)
''')

# Function to parse log files and insert into the database
def parse_log_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            date_part = filename.split('_')[3]
            try:
                entry_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y-%m-%d')
            except ValueError:
                print(f"Filename {filename} contains an invalid date format.")
                continue

            with open(file_path, 'r') as file:
                for line in file:
                    if failed_pattern.search(line):
                        source_name = filename.split('_')[2]  # Assuming the source_name is part of the filename
                        message = line.strip()
                        cur.execute('''
                            INSERT INTO log_entries_idl (log_file, log_entry, entry_date, source_name, message)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (filename, line.strip(), entry_date, source_name, message))

# Parse the log files and insert the data
parse_log_files(log_directory)
conn.commit()

# Update the SQL Query
query = '''
WITH DistinctDates AS (
    SELECT DISTINCT check_date
    FROM check_files_idl
    ORDER BY check_date DESC
    LIMIT 30
)
SELECT c.source_name, c.check_date, c.status, l.message
FROM check_files_idl c
LEFT JOIN log_entries_idl l
ON c.source_name = l.source_name AND c.check_date = l.entry_date
WHERE c.check_date IN (SELECT check_date FROM DistinctDates)
ORDER BY c.check_date
'''

# Read data from the database
df = pd.read_sql_query(query, conn)
conn.close()

# Print the first few rows to verify messages
print(df.head())

# Prepare the data
df['check_date'] = pd.to_datetime(df['check_date'])
df['status_str'] = df['status'].astype(str)  # Convert status to string for color mapping
df = df.sort_values(by='check_date')
source = df

# Create a color mapper
status_list = df['status'].astype(str).unique().tolist()  # Convert to string for color mapping
color_map = factor_cmap('status_str', palette=Spectral6, factors=status_list)

# Create the figure
p = figure(
    x_axis_type='datetime',
    x_axis_label='Check Date',
    y_range=sorted(df['source_name'].unique().tolist(), reverse=True),  # Unique and sorted source names
    y_axis_label='Source Name',
    title='IDL Health Check Status Over Time',
    height=4000,
    width=1200,
    tools="pan,wheel_zoom,box_zoom,reset"
)

# Add circle glyphs to the plot
circle = p.circle(
    x='check_date',
    y='source_name',
    size=10,
    source=source,
    color=color_map,
    legend_field='status_str'
)

# Add HoverTool to display information on hover
hover = HoverTool(
    tooltips=[
        ("Date", "@check_date{%F}"),
        ("Source", "@source_name"),
        ("Status", "@status"),
        ("Message", "@message")
    ],
    formatters={
        '@check_date': 'datetime'
    },
    mode='mouse'
)

p.add_tools(hover)

# Customize the plot
p.yaxis.major_label_orientation = 0
p.legend.title = 'Status'

# Save the plot as HTML
output_file("idl_health_check_status.html")
save(p)

# Convert the HTML file to PNG using html2image
hti = Html2Image()
hti.screenshot(html_file='idl_health_check_status.html', save_as='idl_health_check_status.png')

# Show the plot
show(p)