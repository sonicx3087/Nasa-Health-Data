import sqlite3
from datetime import datetime

def query_instruments_with_status(status, start_date, end_date):
    conn = sqlite3.connect('check_files.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT DISTINCT instrument
        FROM check_files_python
        WHERE status = ? AND check_date BETWEEN ? AND ?
    ''', (status, start_date, end_date))
    results = cur.fetchall()
    conn.close()
    return results

# Example usage
start_date = '2023-06-10'
end_date = '2023-08-09'
status = 9
instruments = query_instruments_with_status(status, start_date, end_date)
print(instruments)
