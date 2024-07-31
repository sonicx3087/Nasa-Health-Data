
import os
import re
import sqlite3
from datetime import datetime
import pandas as pd
from bokeh.plotting import figure, output_file, save, show
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool
from bokeh.palettes import Spectral6

# Directory containing the log files
log_directory = '/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_logs_python'

# Patterns to match lines containing error/warning messages and source name
error_warning_pattern = re.compile(r'(FAILED|WARNING|ERROR).*', re.IGNORECASE)
source_name_pattern = re.compile(r'Query: (\w+) \| (\w+) \| (\w+)', re.IGNORECASE)

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
cur = conn.cursor()

# Create or replace the log_entries_python table
cur.execute('''
CREATE TABLE IF NOT EXISTS log_entries_python (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_file TEXT NOT NULL,
    log_entry TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    source_name TEXT,
    error_message TEXT
)
''')

# Function to parse log files and insert into the database
def parse_log_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            date_part = filename.split('_')[2]  # Extract date from filename
            try:
                entry_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y-%m-%d')
            except ValueError:
                print(f"Filename {filename} contains an invalid date format.")
                continue

            with open(file_path, 'r') as file:
                for line in file:
                    source_match = source_name_pattern.search(line)
                    if source_match:
                        provider, source, instrument = source_match.groups()
                        source_name = f"{provider}-{source}-{instrument}"
                        error_message = line.strip()
                        cur.execute('''
                            INSERT INTO log_entries_python (log_file, log_entry, entry_date, source_name, error_message)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (filename, line.strip(), entry_date, source_name, error_message))

# Parse the log files and insert the data
parse_log_files(log_directory)
conn.commit()

# Query to get data for the Bokeh plot
query = '''
WITH DistinctDates AS (
    SELECT DISTINCT check_date
    FROM check_files_python
    ORDER BY check_date DESC
    LIMIT 30
)
SELECT
    c.source_name,
    c.check_date,
    c.status,
    GROUP_CONCAT(l.error_message, '\n') as error_message
FROM check_files_python c
LEFT JOIN log_entries_python l
ON c.source_name = l.source_name AND c.check_date = l.entry_date
WHERE c.check_date IN (SELECT check_date FROM DistinctDates)
GROUP BY c.source_name, c.check_date, c.status
ORDER BY c.check_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

# Prepare the data for Bokeh
df['check_date'] = pd.to_datetime(df['check_date'])
df['status_str'] = df['status'].astype(str)
source = df

# Create a color mapper
status_list = df['status_str'].unique().tolist()
color_map = factor_cmap('status_str', palette=Spectral6, factors=status_list)

# Create the figure
p = figure(
    x_axis_type='datetime',
    x_axis_label='Check Date',
    y_range=sorted(df['source_name'].unique().tolist()),
    y_axis_label='Source Name',
    title='Python Health Check Status Over Time',
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
        ("Source Name", "@source_name"),
        ("Status", "@status"),
        ("Message", "@error_message")
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

# Save the plot as HTML and display it
output_file("py_health_check_status.html")
save(p)
show(p)
