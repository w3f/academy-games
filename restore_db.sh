#!/bin/bash

# Database details
DB_NAME="django_db"
DB_USER="postgres"
DB_PASSWORD=$DB_PASS
DB_HOST="localhost"
DB_PORT="5432"

# Check if backup file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"

# Check if the specified backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE not found."
    exit 1
fi

# Set PGPASSWORD environment variable for authentication
export PGPASSWORD=$DB_PASSWORD

# Restore the database from the backup file
echo "Restoring database from backup..."
pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --clean $BACKUP_FILE

# Unset the PGPASSWORD environment variable
unset PGPASSWORD

echo "Database restored from backup: $BACKUP_FILE"

