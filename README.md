# Nasa-Health-Data
Working on Pulling Data from the Health Report into a database.

VSO means Virtual Solar Observatory. It is used to search for data stored in many different locations around the world. Users send queries to the Virtual Solar Observatory (VSO). The VSO then interprets the query and sends queries to data providers. 

VSO data has three main identifiers: Provider, Source and Instrument.  

A Provider is generally an institution like the High Altitude Observatory (HAO) or the European Space Agency (ESA).Providers also make data available to the public. A 

Source can be a spacecraft, or an observatory, or other observational facility.

An Instrument is the device that actually takes the data.

The triple Provider-Source-Instrument is unique.


The VSO Health Report summarizes the performance of the VSO in searching for and downloading data from data providers. The Health report is here: https://docs.virtualsolar.org/wiki/VSOHealthReport .

The health report code is run at least once a day to determine if data is searchable and downloadable. Both the SunPy/Fido and IDL/Solarsoft client codes are used to determine if data are searchable and downloadable.

The project is to take the check files and create a database that stores the results. The advantage of using a database is that many more questions can be asked of the check file results.

The first part of the project is to:
Create a database that can store the check files.
Fill the database with the existing check file results.
Use bokeh to recreate the existing summary plots on the VSO health report.

I want to be able to search the database using values to Provider, Source, Instrument, Status and also over time-ranges. An example search could be “give me all the Instruments that had status 9 between 2023 June 10 and 2023 August 9.”

The second part of the project is to
Parse the log files to extract the error/warning when a VSO search/download failed.
Add that to the correct place in the database
Adapt the health report plots to include information on the extracted error/warning
