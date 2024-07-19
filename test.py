import os
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from html2image import Html2Image

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')
query = '''
SELECT source_name, check_date, status
FROM check_files_python
ORDER BY id DESC
LIMIT 30
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
    x_range=df['source_name'].tolist(),
    x_axis_label='Source Name',
    y_axis_label='Check Date',
    title='Health Check Status Over Time',
    height=600,
    width=1200
)

# Add circle glyphs to the plot
p.circle(
    x='source_name',
    y='check_date',
    size=10,
    source=source,
    color=color_map,
    legend_field='status_str'
)

# Customize the plot
p.xaxis.major_label_orientation = 1.2
p.legend.title = 'Status'

# Save the plot as HTML
output_file("health_check_status.html")
save(p)

# Convert the HTML file to PNG using html2image
hti = Html2Image()
hti.screenshot(html_file='health_check_status.html', save_as='health_check_status.png')