#!/bin/bash

mb_container_name=mb-test-db-1
cruise_container_name=mb-cruise-test-1

docker container stop $mb_container_name
docker container stop $cruise_container_name