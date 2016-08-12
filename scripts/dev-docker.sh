#!/bin/bash

RUNNING=$(docker inspect -f {{.State.Running}} acs 2> /dev/null) 

if [ "$?" -ne "0" ]
then
  docker run -it -v ~/.ssh:/root/.ssh -v ~/.acs:/root/.acs -v $(pwd):/src --name acs acs
  exit 0
fi

if [ -z $RUNNING ] || [ "$RUNNING" == "true" ]
then
  echo "Connecting to running 'acs' container"
  docker exec -it acs bash
else
  echo "Re-starting and connecting to an 'acs' container"
  docker start acs
  docker exec -it acs bash
fi


