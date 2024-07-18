import sqlite3
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import BasicTicker, PrintfTickFormatter, Legend
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10
from bokeh.charts import HeatMap

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

# Prepare data for HeatMap
heatmap_data = pd.pivot_table(df, values='status', index='check_date', columns='source_name')

# Create a Bokeh HeatMap
output_file("health_check_heatmap.html")
hm = HeatMap(heatmap_data, title="Health Check Heatmap", width=800)

# Show the HeatMap
show(hm)
