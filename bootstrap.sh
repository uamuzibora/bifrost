#!/bin/sh

# This script is intended to be parsed by Boto and used as part of Boto's run_instance method.
# It is *not* intended to run independently of Boto!

set -e

COMMIT_ID=$py_commit_id
DB_ROOT_PASSWORD=$py_db_root_password

# Check to see if COMMIT_ID was set
if [ -z $$COMMIT_ID ]
	then
		echo "ERROR: No commit ID specified! Quitting."
		echo "Usage: ./bootstrap.sh <git commit id> <mysql root password>"
    	exit 2
fi

if [ -z $$DB_ROOT_PASSWORD ]
	then
		echo "ERROR: No MySQL password specified! Quitting."
		echo "Usage: ./bootstrap.sh <git commit id> <mysql root password>"
    	exit 2
fi


echo "Changing into /opt/nafasi"
cd /opt/nafasi

# Update Git repo and checkout the specified commit
echo "Updating Git remotes..."
git remote update
echo "Executing git pull..."
git pull --all
echo "Checking out $$COMMIT_ID..."
git checkout $$COMMIT_ID
git reset --hard

# Check to see if we've successfully got the commit we wanted
CURRENT_COMMIT_ID=`git rev-parse HEAD`

if [ "$$COMMIT_ID" != "$$CURRENT_COMMIT_ID" ]
	then
		echo "ERROR: Checked out commit ($$CURRENT_COMMIT_ID) does not match specified commit ($$COMMIT_ID). Quitting."
		exit 2
fi

# Copy our new version of OpenMRS into Tomcat's webapps directory
sudo -u tomcat7 cp -R /opt/nafasi/openmrs /var/lib/tomcat7/webapps/openmrs

# Update MySQL
echo "Dropping existing openmrs db..."
mysql -u root --password=$$DB_ROOT_PASSWORD -e "DROP DATABASE IF EXISTS openmrs;"
echo "Creating new openmrs db..."
mysql -u root --password=$$DB_ROOT_PASSWORD -e "CREATE DATABASE openmrs CHARACTER SET utf8;"
echo "Importing MySQL dump from Nafasi repo..."
mysql -u root --password=$$DB_ROOT_PASSWORD -e "SET FOREIGN_KEY_CHECKS = 0; USE openmrs; SOURCE /opt/nafasi/sql/openmrs.sql; SET FOREIGN_KEY_CHECKS = 1;"

# Start Tomcat
echo "(Re)Starting Tomcat..."
/etc/init.d/tomcat7 restart
echo "Cue the funky music, we're live!"

exit