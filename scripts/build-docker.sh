#!/bin/bash

docker stop acs
docker rm acs
docker build -t acs .
