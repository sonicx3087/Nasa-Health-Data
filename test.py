import os
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save, show
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral6
from html2image import Html2Image

# Function to load and filter log file messages
def load_log_file(log_file_path):
    with open(log_file_path, 'r') as file:
        log_lines = file.readlines()

    log_data = []
    for line in log_lines:
        if 'Random query failed. Attempting known query for' in line:
            parts = line.split(': ')
            if len(parts) > 1:
                source_name = parts[1].split(', ')[0]
                log_data.append({
                    'source_name': source_name,
                    'message': line.strip()
                })

    log_df = pd.DataFrame(log_data)
    print(log_df)
    return log_df


# Load multiple log files
log_directory = '/Users/dokigbo/Downloads/vso_health_summer_project/vso_health_logs_idl'  # Update this path
log_files = [os.path.join(log_directory, f) for f in os.listdir(log_directory) if f.endswith('.log')]
log_dfs = [load_log_file(log_file) for log_file in log_files]
combined_log_df = pd.concat(log_dfs).drop_duplicates().reset_index(drop=True)

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')

# Query to get data with 30 distinct check_date values
query = '''
WITH DistinctDates AS (
    SELECT DISTINCT check_date
    FROM check_files_idl
    ORDER BY check_date DESC
    LIMIT 30
)
SELECT source_name, check_date, status
FROM check_files_idl
WHERE check_date IN (SELECT check_date FROM DistinctDates)
ORDER BY check_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

# Prepare the data
df['check_date'] = pd.to_datetime(df['check_date'])
df['status_str'] = df['status'].astype(str)  # Convert status to string for color mapping

# Merge log messages with the main DataFrame
df = pd.merge(df, combined_log_df, on='source_name', how='left')

# Ensure unique data points based on check_date and source_name
df = df.drop_duplicates(subset=['check_date', 'source_name'])

# Sort data for plotting
df = df.sort_values(by='check_date')
source = ColumnDataSource(df)

# Create a color mapper
status_list = df['status'].astype(str).unique().tolist()  # Convert to string for color mapping
color_map = factor_cmap('status_str', palette=Spectral6, factors=status_list)

# Create the figure
p = figure(
    x_axis_type='datetime',
    x_axis_label='Check Date',
    y_range=sorted(df['source_name'].unique().tolist()),  # Unique and sorted source names
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
        ("Instrument", "@source_name"),
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