# Nasa-Health-Data
Working on Pulling Data from the Health Report into a database.

There are 4 tables in the vso_files.db database

These tables are: 
check_files_idl     check_files_python  log_entries_idl     log_entries_python


check_files_idl

The fields in the  check_files_idl table are 

0|id|INTEGER|0||1 
1|provider|TEXT|1||0
2|source|TEXT|1||0
3|instrument|TEXT|1||0
4|source_name|TEXT|1||0
5|status|INTEGER|0||0
6|check_date|TEXT|0||0
7|message|TEXT|0||0


id is just auto incrimented

provider,source, and instrument are self explanatory

source_name is the identifier basically the provider, souce, and instrument together.

check_date is the date contained on each of the filenames

message in this table is empty and could be removed.

The code that produces this table is named as of 8/9/14 populate_database_idl.py

populate_database_idl store the csv files that were in the vso_health_checks_idl directory

The Next Table is check_files_python

The fields in this table are 

0|id|INTEGER|0||1
1|provider|TEXT|1||0
2|source|TEXT|1||0
3|instrument|TEXT|1||0
4|source_name|TEXT|1||0
5|status|INTEGER|0||0
6|check_date|TEXT|0||0

See check_files_idl table explanation to explain what they mean.

The code that produces this table is named as of 8/9/14 populate_database.py

populate_database.py store the csv files that were in the vso_health_checks_python directory


The next table is log_entries_idl

The fields in this table are:

0|id|INTEGER|0||1
1|log_file|TEXT|1||0
2|log_entry|TEXT|1||0
3|entry_date|TEXT|1||0
4|source_name|TEXT|0||0
5|message|TEXT|0||0

id abd source_name are explained in other tables

log_file just store the log_file names in the vso_health_logs_idl directory. This could probably be removed

log_entry and message produce the same thing and one of these could be removed. They both look for the the word failed in the log files contained in the vso_health_logs_idl directory.

entry_date are just the dates contained on the log_files in the directory

and source_name has been explained in other tables

As of 8/9/24 the code that produces this tbale is called idl_logs.py

The final table is called log_entries_python

As of 8/9/24 the code that produces this table is called python_logs

the fields in this table are called

0|id|INTEGER|0||1
1|log_file|TEXT|1||0
2|log_entry|TEXT|1||0
3|entry_date|TEXT|1||0
4|source_name|TEXT|0||0
5|error_message|TEXT|0||0

log_entry and error_message sort of share the same purpose. They are meant to display the messages in the idl logs associated with the right source name on the right date. I believe error_message field does this better as in it gets more messages.

checkpy_plot.py produced a plot that is accurate for the health report with the correct messages

checkidl_plot produces a plot that is accurate for the health report but displays no messages