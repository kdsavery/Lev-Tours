# Version 1.2
import logging
import os
from datetime import date

# Set up logging for events and to track positions
LOG_DIRECTORY = "logging"
LOG_DIRECTORY = os.path.join(os.getcwd(), LOG_DIRECTORY)
if(not os.path.isdir(LOG_DIRECTORY)):
	os.mkdir(LOG_DIRECTORY)

# Determine what the name of this log file will be,
# every log will include the date and an index
today = str(date.today())
dates = os.listdir(LOG_DIRECTORY) # Dates that contain log files
date_directory = os.path.join(LOG_DIRECTORY, today)
today_cnt = 0
if(today in dates):
	logs = os.listdir(date_directory)
	for log in logs:
		# Extract data, format: tour_app_DATE_index.txt
		date = log.split("_")[2]
		if(date == today):
			today_cnt += 1
else:	
	os.mkdir(date_directory)

# Increment today cnt to prepare a new log file
today_cnt += 1
log_file = "tour_app_" + str(today) + "_" + str(today_cnt) + ".txt"
log_path = os.path.join(date_directory, log_file)

# Formatting the log file output
LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(filename)s:%(lineno)d")
logging.basicConfig(format=LOG_FORMAT, 
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=log_path,
                    level=logging.INFO)