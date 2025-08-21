#!/bin/bash

set -ex

cd /home/oracle
mkdir -p data

# BOOTSTRAP MB USER:
sqlplus SYSTEM/Iwantinnow1@XEPDB1 @/home/oracle/setup-files/setup-user.sql

# MIGRATE MB DB:
sqlplus MB/letmein@XEPDB1 @/home/oracle/setup-files/create_mb.sql
