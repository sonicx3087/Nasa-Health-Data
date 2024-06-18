import sqlite3
from datetime import datetime

def get_instruments_by_status_and_date(status, start_date, end_date):
    conn = sqlite3.connect('check_files.db')
    cursor = conn.cursor()

    query = '''
    SELECT ds.source_name, sr.status, sr.status_date
    FROM status_records sr
    JOIN data_sources ds ON sr.data_source_id = ds.id
    WHERE sr.status = ? AND sr.status_date BETWEEN ? AND ?
    '''
   
    cursor.execute(query, (status, start_date, end_date))
    results = cursor.fetchall()
   
    conn.close()
   
    return results

# Example usage
status = 9
start_date = '2023-06-10'
end_date = '2023-08-09'
instruments = get_instruments_by_status_and_date(status, start_date, end_date)

for instrument in instruments:
    print(instrument)