-- Create the main table for storing the check file data
CREATE TABLE data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT UNIQUE
);


-- Create a table to store the status records
CREATE TABLE status_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source_id INTEGER,
    status INTEGER,
    status_date DATE,
    FOREIGN KEY (data_source_id) REFERENCES data_sources (id)
);