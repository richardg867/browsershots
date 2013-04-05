#!/bin/sh
date

echo "Counting yesterday's screenshots..."
sudo -u johann shotserver04_uploads_by_factory.py
date

SQLBZ2=/backup/shotserver04.`date +%Y-%m-%d`.sql.bz2
if [ -s $SQLBZ2 ]; then
    echo "Found existing database backup for today, skipping."
else
    echo "Dumping database for backup..." &&
    sudo -u postgres pg_dump shotserver04 | bzip2 > $SQLBZ2
    date
fi

echo "Deleting old entries from database..."
sudo -u postgres psql shotserver04 \
< /home/johann/checkout/shotserver/shotserver04_cleanup.sql
date

echo "Vacuuming all databases..."
sudo -u postgres vacuumdb --all --analyze
date
