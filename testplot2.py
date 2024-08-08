import os
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save, show
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral6
from html2image import Html2Image

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
SELECT c.source_name, c.check_date, c.status, l.log_entry as message
FROM check_files_idl c
LEFT JOIN log_entries_idl l
ON c.check_date = l.entry_date
WHERE c.check_date IN (SELECT check_date FROM DistinctDates)
ORDER BY c.check_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

# Prepare the data
df['check_date'] = pd.to_datetime(df['check_date'])
df['status_str'] = df['status'].astype(str)  # Convert status to string for color mapping
df = df.sort_values(by='check_date')
source = ColumnDataSource(df)

# Create a color mapper
status_list = df['status'].astype(str).unique().tolist()  # Convert to string for color mapping
color_map = factor_cmap('status_str', palette=Spectral6, factors=status_list)

# Create the figure
p = figure(
    x_axis_type='datetime',
    x_axis_label='Check Date',
    y_range=sorted(df['source_name'].unique().tolist(), reverse=True),  # Unique and sorted source names in reverse order
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
output_file("idl_health_checktest.html")
save(p)

# Convert the HTML file to PNG using html2image
hti = Html2Image()
hti.screenshot(html_file='idl_health_checktest.html', save_as='idl_health_checktest.png')

# Show the plot
show(p)
