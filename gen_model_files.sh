#! /bin/bash

PRISM_BENCHMARKS="/home/jantsch/prism-benchmarks"
PRISM="/home/jantsch/prism/prism/bin/prism"

#dtmcs

for i in {32,64,128,512,1024}; do for j in {2..2}; do $PRISM  $PRISM_BENCHMARKS/models/dtmcs/brp/brp.pm $PRISM_BENCHMARKS/models/dtmcs/brp/p2.pctl -const N=$i,MAX=$j -exportmodel ./dtmc_benchmarks/brp_files/brp-$i-$j.tra,sta,lab; done; done

for j in {2..7}; do for i in {3..10}; do $PRISM $PRISM_BENCHMARKS/models/dtmcs/crowds/crowds.pm $PRISM_BENCHMARKS/models/dtmcs/crowds/positive.pctl -const TotalRuns=$i,CrowdSize=$j -exportmodel ./dtmc_benchmarks/crowds_files/crowds-$j-$i.tra,sta,lab; done; done

for j in {3..6}; do for i in {2..8}; do $PRISM $PRISM_BENCHMARKS/models/dtmcs/leader_sync/leader_sync$j\_$i.pm $PRISM_BENCHMARKS/models/dtmcs/leader_sync/eventually_elected.pctl -exportmodel ./dtmc_benchmarks/leader_files/leader-$j-$i.tra,sta,lab; done; done

#mdps
for j in {2,4}; do for i in {2,4}; do $PRISM $PRISM_BENCHMARKS/models/mdps/consensus/coin$j.nm $PRISM_BENCHMARKS/models/mdps/consensus/c1.pctl -const K=$i -exportmodel ./mdp_benchmarks/consensus_files/consensus-$j-$i.tra,sta,lab; done; done

echo "\"eventually_all_delivered\": Pmin=? [F \"all_delivered\"] " > $PRISM_BENCHMARKS"/models/mdps/csma/all_delivered.pctl"

for j in {2..4}; do for i in {2,4,6}; do $PRISM $PRISM_BENCHMARKS/models/mdps/csma/csma$j\_$i.nm $PRISM_BENCHMARKS/models/mdps/csma/all_delivered.pctl -exportmodel ./mdp_benchmarks/csma_files/csma-$j-$i.tra,sta,lab,dot; done; done
