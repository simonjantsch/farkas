#! /bin/bash

PRISM_BENCHMARKS="/home/jantsch/prism-benchmarks"
PRISM="/home/jantsch/prism/prism/bin/prism"

#dtmcs

mkdir -p ./dtmc_benchmarks/brp_files/

cp $PRISM_BENCHMARKS/models/dtmcs/brp/brp.pm ./dtmc_benchmarks/brp_files/brp.pm
echo "label \"uncertain\" = s=5 & srep=2;" >> ./dtmc_benchmarks/brp_files/brp.pm

for i in {32,64,128,512,1024,2048}; do for j in {2..2}; do $PRISM ./dtmc_benchmarks/brp_files/brp.pm $PRISM_BENCHMARKS/models/dtmcs/brp/p2.pctl -const N=$i,MAX=$j -exportmodel ./dtmc_benchmarks/brp_files/brp-$i-$j.tra,sta,lab; done; done

mkdir -p ./dtmc_benchmarks/crowds_files/

cp $PRISM_BENCHMARKS/models/dtmcs/crowds/crowds.pm ./dtmc_benchmarks/crowds_files/crowds.pm
echo "label \"bad\" = observe0 > 1;" >> ./dtmc_benchmarks/crowds_files/crowds.pm

for j in {2..5}; do for i in {3..12}; do $PRISM ./dtmc_benchmarks/crowds_files/crowds.pm $PRISM_BENCHMARKS/models/dtmcs/crowds/positive.pctl -const TotalRuns=$i,CrowdSize=$j -exportmodel ./dtmc_benchmarks/crowds_files/crowds-$j-$i.tra,sta,lab; done; done

mkdir -p ./dtmc_benchmarks/leader_files/

for j in {3..6}; do for i in {2..6}; do $PRISM $PRISM_BENCHMARKS/models/dtmcs/leader_sync/leader_sync$j\_$i.pm $PRISM_BENCHMARKS/models/dtmcs/leader_sync/eventually_elected.pctl -exportmodel ./dtmc_benchmarks/leader_files/leader-$j-$i.tra,sta,lab; done; done

~/anaconda3/bin/python3.7 gen_comics_models.py

# #mdps
mkdir -p ./mdp_benchmarks/consensus_files/

for j in {2,4}; do for i in {2,4}; do $PRISM $PRISM_BENCHMARKS/models/mdps/consensus/coin$j.nm $PRISM_BENCHMARKS/models/mdps/consensus/c1.pctl -const K=$i -exportmodel ./mdp_benchmarks/consensus_files/consensus-$j-$i.tra,sta,lab; done; done

echo "\"eventually_all_delivered\": Pmin=? [F \"all_delivered\"] " > $PRISM_BENCHMARKS"/models/mdps/csma/all_delivered.pctl"

mkdir -p ./mdp_benchmarks/csma_files

for j in {2..2}; do for i in {2,4,6}; do $PRISM $PRISM_BENCHMARKS/models/mdps/csma/csma$j\_$i.nm $PRISM_BENCHMARKS/models/mdps/csma/all_delivered.pctl -exportmodel ./mdp_benchmarks/csma_files/csma-$j-$i.tra,sta,lab; done; done

for j in {3..3}; do for i in {2,4}; do $PRISM $PRISM_BENCHMARKS/models/mdps/csma/csma$j\_$i.nm $PRISM_BENCHMARKS/models/mdps/csma/all_delivered.pctl -exportmodel ./mdp_benchmarks/csma_files/csma-$j-$i.tra,sta,lab; done; done

for j in {4..4}; do for i in {2..2}; do $PRISM $PRISM_BENCHMARKS/models/mdps/csma/csma$j\_$i.nm $PRISM_BENCHMARKS/models/mdps/csma/all_delivered.pctl -exportmodel ./mdp_benchmarks/csma_files/csma-$j-$i.tra,sta,lab; done; done
