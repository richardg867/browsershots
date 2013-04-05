#!/bin/sh
PGBIN=/usr/bin
PYTHON=python

echo "DELETE FROM django_site;" > django_site.modified.sql
cat django_site.sql >> django_site.modified.sql

$PYTHON date_filter.py 2008-05-09 \
< screenshots_screenshot.sql \
> screenshots_screenshot.modified.sql

$PYTHON date_filter.py 2008-05-10 \
< requests_request.sql \
> requests_request.modified.sql

$PYTHON date_filter.py 2008-05-13 \
< messages_factoryerror.sql \
> messages_factoryerror.modified.sql

grep -v 567996 \
< websites_website.sql \
> websites_website.modified.sql

grep -v 567996 \
< requests_requestgroup.sql \
> requests_requestgroup.modified.sql

cat screenshots_problemreport.sql \
| ./date_filter.py 2008-05-15 \
| grep -v 9250049 \
> screenshots_problemreport.modified.sql

$PGBIN/dropdb shotserver04
$PGBIN/createdb shotserver04
$PYTHON ../shotserver04new/manage.py syncdb --noinput
$PYTHON load_tables.py $PGBIN
