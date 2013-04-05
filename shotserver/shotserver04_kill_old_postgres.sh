#!/bin/sh
echo "SELECT procpid, current_query FROM pg_stat_activity
WHERE backend_start < NOW() - '1:00'::interval" \
| sudo -u postgres psql template1 \
| grep IDLE | cut -d\| -f1 \
| sudo xargs --no-run-if-empty kill
