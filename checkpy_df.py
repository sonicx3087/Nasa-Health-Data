import sqlite3
import pandas as pd
from bokeh.io import output_file, show, export_png
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter, Legend, Title
from bokeh.plotting import figure
from bokeh.transform import transform, factor_cmap
from html2image import Html2Image
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('vso_files.db')

# Query the data from the database
query = """
SELECT provider, source, instrument, check_date, status
FROM check_files_python
"""
df = pd.read_sql(query, conn)
conn.close()

# Convert check_date to datetime
df['check_date'] = pd.to_datetime(df['check_date'])

# Prepare data for plotting
df['source_name'] = df['provider'] + '-' + df['source'] + '-' + df['instrument']

# Creating a ColumnDataSource
source = ColumnDataSource(df)

# Create a Bokeh plot
p = figure(
    title="Health Check Data",
    x_axis_label='Check Time',
    y_axis_label='Provider-Source-Instrument',
    x_axis_type='datetime',
    plot_width=800,
    plot_height=600
)

# Add circles for the data points
p.circle(
    x='check_date',
    y='source_name',
    size=10,
    source=source,
    legend_field='source_name'
)

# Configure x-axis to have intervals of 30 days
p.xaxis.ticker = BasicTicker(desired_num_ticks=int((df['check_date'].max() - df['check_date'].min()).days / 30))
p.xaxis.formatter = PrintfTickFormatter(format="%Y-%m-%d")

# Add color bar if needed
color_mapper = LinearColorMapper(palette="Viridis256", low=df['status'].min(), high=df['status'].max())
color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(), formatter=PrintfTickFormatter(format="%d"))
p.add_layout(color_bar, 'right')

# Add title and other layout properties
p.title.align = "center"
p.title.text_font_size = "20px"
p.legend.orientation = "horizontal"
p.legend.location = "top_center"

# Show the plot
output_file("health_check_plot.html")
show(p)

# Optionally, export the plot as PNG
hti = Html2Image()
hti.screenshot(html_file='health_check_plot.html', save_as='health_check_plot.png')
