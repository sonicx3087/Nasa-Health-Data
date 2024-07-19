import sqlite3
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import BasicTicker, ColumnDataSource, PrintfTickFormatter, Legend, ColorBar
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')

# Fetch data from the database
query = '''
SELECT provider, source, instrument, check_date, status
FROM check_files_python
'''

df = pd.read_sql(query, conn)

# Close the connection
conn.close()

# Convert check_date to datetime format
df['check_date'] = pd.to_datetime(df['check_date'])

# Combine provider, source, and instrument into a single column for the y-axis
df['source_name'] = df['provider'] + '-' + df['source'] + '-' + df['instrument']

# Creating a ColumnDataSource
source = ColumnDataSource(df)

# Define unique statuses and corresponding colors
unique_statuses = df['status'].unique().astype(str)
status_colors = Category10[len(unique_statuses)]  # Use a suitable palette for the number of unique statuses

# Create a Bokeh plot
p = figure(
    title="Health Check Data",
    x_axis_label='Check Time',
    y_axis_label='Provider-Source-Instrument',
    x_axis_type='datetime',
    width=800,
    height=600
)

# Add circles for the data 
p.circle(
    x='check_date',
    y='source_name',
    size=10,
    source=source,
    legend_field='status',
    color=factor_cmap('status', palette=status_colors, factors=unique_statuses)
)

# Configure x-axis to have intervals of 30 days
p.xaxis.ticker = BasicTicker(desired_num_ticks=int((df['check_date'].max() - df['check_date'].min()).days / 30))
p.xaxis.formatter = PrintfTickFormatter(format="%Y-%m-%d")

# Add title and other layout properties
p.title.align = "center"
p.title.text_font_size = "20px"
p.legend.orientation = "horizontal"
p.legend.location = "top_center"
p.legend.title = "Status"

# Show the plot
output_file("health_check_plot.html")
show(p)