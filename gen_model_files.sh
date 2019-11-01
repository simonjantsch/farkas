#! /bin/bash

PRISM_BENCHMARKS = "~/devel/prism-benchmarks"
PRISM = "~/devel/prism-farkas/prism/bin/prism"

#dtmcs

for i in {32,64,128,512}; do for j in {2..4}; do  $PRISM_BENCHMARKS/models/dtmcs/brp/brp.pm $PRISM_BENCHMARKS/models/dtmcs/brp/p2.pctl -const N=$i,MAX=$j -exportmodel brp-$i-$j.tra,sta,lab; done; done

for j in {2..5}; do for i in {3..8}; do $PRISM $PRISM_BENCHMARKS/models/dtmcs/crowds/crowds.pm $PRISM_BENCHMARKS/models/dtmcs/crowds/positive.pctl -const TotalRuns=$i,CrowdSize=$j -exportmodel crowds-$j-$i.tra,sta,lab; done; done

for j in {3..6}; do for i in {2..6}; do $PRISM $PRISM_BENCHMARKS/models/dtmcs/leader_sync/leader_sync$j_$i.pm $PRISM_BENCHMARKS/models/dtmcs/leader_sync/eventually_elected.pctl -exportmodel leader-$j-$i.tra,sta,lab; done; done

#mdps
for j in {2,4}; do for i in {2,4}; do $PRISM $PRISM_BENCHMARKS/models/mdps/consensus/coin$j.nm $PRISM_BENCHMARKS/models/mdps/consensus/c1.pctl -const K=$i -exportmodel consensus-$j-$i.tra,sta,lab; done; done

for j in {2..4}; do for i in {2,4,6}; do $PRISM $PRISM_BENCHMARKS/models/mdps/csma/csma$j\_$i.nm $PRISM_BENCHMARKS/models/mdps/csma/all_delivered.pctl -exportmodel csma-$j-$i.tra,sta,lab,dot; done; done
