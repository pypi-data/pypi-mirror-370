#!/usr/bin/env bash


nohup "./run.sh" > /dev/null 2>&1 &
echo $! > "$PWD/run.pid"

exit 0