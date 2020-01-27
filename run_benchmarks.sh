#! /bin/bash
set -x

DATE=$(date +"%d%m_%H%M")
BASE_DIR="benchmark_runs/$DATE/"
mkdir $BASE_DIR

# run DTMC benchmarks

if [ $1 == "dtmc" ]
then
    mkdir $BASE_DIR"crowds/"
    mkdir $BASE_DIR"leader/"
    mkdir $BASE_DIR"brp/"

    nohup taskset -c 0-3 ./run.sh bench_crowds.py $BASE_DIR"crowds/" &
    nohup taskset -c 4-7 ./run.sh bench_leader.py $BASE_DIR"leader/" &
    nohup taskset -c 8-11 ./run.sh bench_brp.py $BASE_DIR"brp/" &
fi

if [ $1 == "mdp" ]
then
    mkdir $BASE_DIR"consensus/"
    mkdir $BASE_DIR"csma/"

    nohup taskset -c 0-3 ./run.sh bench_consensus.py $BASE_DIR"consensus/" &
    nohup taskset -c 4-7 ./run.sh bench_csma.py $BASE_DIR"csma/" &
fi

if [ $1 == "other" ]
then
    mkdir $BASE_DIR"consensus/"
    
    nohup taskset -c 0-3 ./run.sh bench_consensus.py $BASE_DIR"consensus/" &
fi    
