
import os
import re
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save, show
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral6
from textwrap import wrap

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')

# Query to get data with 30 distinct check_date values
#Remove or increase the limit to see more dates
#log_entries_idl is a table in the database and so is check_files_idl
query = '''
WITH DistinctDates AS (
    SELECT DISTINCT check_date
    FROM check_files_idl
    ORDER BY check_date DESC
    LIMIT 30 
)
SELECT
    c.source_name,
    c.check_date,
    c.status,
    l.message as error_message
FROM check_files_idl c
LEFT JOIN log_entries_idl l
ON c.source_name = l.source_name AND c.check_date = l.entry_date
WHERE c.check_date IN (SELECT check_date FROM DistinctDates)
ORDER BY c.check_date
'''

df = pd.read_sql_query(query, conn)
conn.close()

# Group by 'source_name', 'check_date', and 'status', then concatenate unique error messages
df_grouped = df.groupby(['source_name', 'check_date', 'status'])['error_message'].apply(
    lambda x: "<br>".join(wrap("\n".join(x.dropna().unique()), 40))
).reset_index()

# Add custom tooltip messages based on status
#If the status is 2 it gets a specific messagw
def get_tooltip_message(status, error_message):
    if status == 2:
        return "Status is 2 which means it's skipped and therefore no message"
    return error_message

df_grouped['tooltip_message'] = df_grouped.apply(lambda row: get_tooltip_message(row['status'], row['error_message']), axis=1)

# Prepare the data for Bokeh
df_grouped['check_date'] = pd.to_datetime(df_grouped['check_date'])
df_grouped['status_str'] = df_grouped['status'].astype(str)

# Create a color mapper
status_list = df_grouped['status_str'].unique().tolist()
color_map = {
    '1': 'green',  # Pass or known query
    '0': '#32CD32',   # Pass
    '9': 'red',    # Fail no response (no data)
    '8': 'orange', # Fail on download
    '2': 'yellow'    # Skipped
}

df_grouped['color'] = df_grouped['status_str'].map(color_map)

source = ColumnDataSource(df_grouped)

# Create the figure
p = figure(
    x_axis_type='datetime',
    x_axis_label='Check Date',
    y_range=sorted(df_grouped['source_name'].unique().tolist(), reverse=True),
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
    color='color',
    legend_field='status_str'
)

# Add HoverTool with custom tooltips
hover = HoverTool(
    tooltips="""
        <div>
            <div><strong>Date:</strong> @check_date{%F}</div>
            <div><strong>Source Name:</strong> @source_name</div>
            <div><strong>Status:</strong> @status</div>
            <div><strong>Message:</strong> @tooltip_message</div>
        </div>
    """,
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
output_file("idl_health_check_status.html")
save(p)
show(p)

