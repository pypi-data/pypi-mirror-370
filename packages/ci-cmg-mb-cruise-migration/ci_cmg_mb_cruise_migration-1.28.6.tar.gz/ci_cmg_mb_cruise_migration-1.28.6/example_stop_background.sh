#!/usr/bin/env bash

PIDFILE="$PWD/run.pid"

if [[ -f "$PIDFILE" ]]; then
  pid=`cat "$PIDFILE"`
  echo "Sending TERM signal to process $pid"
    kill -- -$(ps -o pgid= $pid | grep -o [0-9]*)
    echo "Verify $pid has been terminated"
    rm "$PIDFILE"
else
  echo "PID file not found $PIDFILE.  If the process is running it may have to be manually killed."
fi

exit 0