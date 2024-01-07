#!/bin/bash

echo "Starting Otree server.."

nohup sudo -E env "PATH=$PATH" otree prodserver 8000 > log.out 2>&1 &

echo $! > otree_pid.txt
