#! /bin/bash
set -x

SCRIPT=$1
DIR=$2

ulimit -Sm $((100*1024*1024))
CURRENT_DIR=$(pwd)
cd $DIR
mkdir "csv"
~/anaconda3/bin/python3.7 "$CURRENT_DIR/$SCRIPT" "$CURRENT_DIR/" &> "logfile"
