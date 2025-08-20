#!/usr/bin/env bash

source ./migenv/bin/activate

python -m src.main.start_migration "$PWD/config.yaml"

exit 0