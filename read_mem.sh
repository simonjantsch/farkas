#!/bin/bash

## Assumes a logfile as produced by the run.sh script as input

FILE=$1

echo "max memory of LP instances (in MiB):"
awk '/Statistics for model/{c=3}c&&c--; /m2.optimize/{print "mem consumption: " $4 " " $5}' $FILE | awk '(/mem consumption/ && f!="Variable") {print $3} {f=$1}' | sort -nr | head -1

echo "max memory of MILP instances (in MiB):"

awk '/Statistics for model/{c=3}c&&c--; /m2.optimize/{print "mem consumption: " $4 " " $5}' $FILE | awk '(/mem consumption/ && f=="Variable") {print $3} {f=$1}' | sort -nr | head -1
