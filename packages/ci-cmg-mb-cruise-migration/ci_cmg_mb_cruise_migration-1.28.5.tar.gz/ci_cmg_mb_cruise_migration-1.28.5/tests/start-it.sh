#!/bin/bash

current_dir=$(pwd)
mb_container_name=mb-test-db-1
cruise_container_name=mb-cruise-test-1

echo "starting docker db's..."
docker run -d --rm --name $mb_container_name -p 15210:1521  -e ORACLE_PDB=XEPDB1 -v "$current_dir/setup-files":/home/oracle/setup-files cirescmg/crowbar-db:20210416
docker run -d --rm --name $cruise_container_name -p 15211:1521 -v "$current_dir/setup-files":/home/oracle/setup-files cirescmg/cruise-db:20210727

echo "................................................................................"
SECONDS=0
mb_status=$(docker ps | grep $mb_container_name)
cruise_status=$(docker ps | grep $cruise_container_name)
until [[ $mb_status == *"(healthy)"* && $cruise_status == *"(healthy)"* ]]
do
  echo -n "*"
  sleep 2
  if (( SECONDS > 160 )); then
     echo -e "\nTIMEOUT: To migrate db manually, run: docker exec --user oracle $mb_container_name /home/oracle/setup-files/setup_mb.sh"
     docker ps
     exit 1
  fi
  mb_status=$(docker ps | grep $mb_container_name)
  cruise_status=$(docker ps | grep $cruise_container_name)
done

echo -e "\ninitiating mb schema..."
set +e
docker exec --user oracle $mb_container_name /home/oracle/setup-files/setup_mb.sh
set -e

echo -e "\nmigrating cruise schema..."
set +e
docker exec --user oracle $cruise_container_name /home/oracle/setup-files/setup_cruise.sh
set -e

docker ps
