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

# Fetch all dates and data from the database
query = '''
SELECT source_name, check_date, status
FROM check_files_python
ORDER BY check_date
'''
df = pd.read_sql_query(query, conn)
conn.close()

# Convert check_date to datetime
df['check_date'] = pd.to_datetime(df['check_date'])

# Define the specific dates to use
specific_dates = [
    '2023-06-02', '2023-06-03', '2023-06-04', '2023-06-05', '2023-06-06',
    '2023-06-07', '2023-06-08', '2023-06-09', '2023-06-10', '2023-06-11',
    '2023-06-12', '2023-06-13', '2023-06-14', '2023-06-15', '2023-06-16',
    '2023-06-17', '2023-06-18', '2023-06-19', '2023-06-20', '2023-06-21',
    '2023-06-22', '2023-06-23', '2023-06-24', '2023-06-25', '2023-06-26',
    '2023-06-27', '2023-06-29', '2023-06-30', '2023-07-02', '2023-07-03',
    '2023-07-04', '2023-07-05', '2023-07-06'
]

# Convert specific_dates to datetime
specific_dates = pd.to_datetime(specific_dates)

# Filter data for the specific dates
filtered_df = df[df['check_date'].isin(specific_dates)]
print(filtered_df)
filtered_df['status_str'] = filtered_df['status'].astype(str)

# Prepare data for plotting
source = ColumnDataSource(filtered_df)
print(source)
status_list = filtered_df['status_str'].unique().tolist()
color_map = factor_cmap('status_str', palette=Spectral6, factors=status_list)

y_range=list(filtered_df['check_date'].unique())
print(y_range)
#x_range=list(reversed(filtered_df['source_name'].unique()))
#print(x_range)

p = figure(width=1400,height=1500,y_range=list(filtered_df['check_date'].to_pydatetime().unique()), x_range=list(reversed(filtered_df['source_name'].unique())))
# Create the figure
'''
p = figure(
    y_range=filtered_df['source_name'].tolist(),
    x_axis_label='Check Date',
    y_axis_label='Source Name',
    title='Health Check Status for Selected Dates',
    height=600,
    width=1200,
    x_axis_type='datetime'
)

# Add circle glyphs to the plot
p.circle(
    x='check_date',
    y='source_name',
    size=10,
    source=source,
    color=color_map,
    legend_field='status_str'
)

# Customize the plot
p.xaxis.major_label_orientation = 1.2
p.legend.title = 'Status'
'''
# Save the plot as HTML
output_file("health_check_stat.html")
save(p)

# Convert the HTML file to PNG using html2image
hti = Html2Image()
hti.screenshot(html_file='health_check_status.html', save_as='health_check_stat.png')
