#!/bin/bash
PYTHON="/usr/bin/python3"
APP_LOCATION="/home/pi/PlexApp"
CRON_FILE=$APP_LOCATION/plex_app/cron_scripts.py
EMAIL="jfalhashash@gmail.com"
RESP=$($PYTHON $CRON_FILE "download")
echo $RESP

if [[ $RESP == File* ]] ;
then
	echo $RESP |
		mail -s "Files Have Been Downloaded" $EMAIL
fi
