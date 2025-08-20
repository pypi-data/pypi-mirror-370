#!/bin/bash

set -ex

cd /home/oracle
mkdir -p data

# MIGRATE CRUISE DB:
sqlplus CRUISE/letmein@XEPDB1 @/home/oracle/setup-files/migrate_cruise.sql
