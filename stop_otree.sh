#!/bin/bash

# Read the PID from the file and kill the process
if [ -f otree_pid.txt ]; then
    kill $(cat otree_pid.txt)
    rm otree_pid.txt
else
    echo "PID file not found. oTree may not be running."
fi

