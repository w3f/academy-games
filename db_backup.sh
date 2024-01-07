#!/bin/bash

# Database details
DB_NAME="django_db"
DB_USER="postgres"
DB_PASSWORD=$DB_PASS
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d%H%M")

# Set PGPASSWORD environment variable for authentication
export PGPASSWORD=$DB_PASSWORD

# Create a backup
pg_dump -Fc -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $BACKUP_DIR/django_db_backup_$DATE.sql

# Unset the PGPASSWORD environment variable
unset PGPASSWORD

echo "Backup created: django_db_backup_$DATE.sql"

