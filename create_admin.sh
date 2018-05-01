#!/bin/bash

# Create role admin if not exists and create hasker db if not exists
tempfile=tmp_`date +"%Y_%m_%d_%H_%M_%S"`
psql -U postgres -c " 
   	DO 
	\$do\$ 
	BEGIN 
		IF EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN 
			RAISE NOTICE 'User admin already exists'; 
		ELSE 
			CREATE ROLE admin with SUPERUSER LOGIN PASSWORD 'admin'; 
			RAISE NOTICE 'User admin has been created';
		END IF;	
		IF EXISTS (SELECT 1 FROM pg_database where datname = 'hasker') THEN 
			RAISE NOTICE 'Database already exists'; 
		END IF; 
	END 
	\$do\$; 
	" &> $tempfile;

if [ -z "`grep 'Database already exists' $tempfile`" ]
then
	psql -U postgres -c "CREATE DATABASE hasker WITH OWNER admin;"
	echo 'Database hasker has been created' >> $tempfile
fi

cat $tempfile
rm $tempfile

