Python implementation to compute Farkas certificates and witnessing subsystems 
for reachability constraints in Markov decision processes.

## Preconditions
* The Gurobi Solver needs to be installed (https://www.gurobi.com/) and its
python interface needs to be set up.
* To build models and validate subsystems, Prism needs to be installed 
(http://www.prismmodelchecker.org/), and prism-benchmarks
(https://github.com/prismmodelchecker/prism-benchmarks) need to be checked-out.
* For comparison scripts with COMICS, the tool needs to be installed
(https://www-i2.informatik.rwth-aachen.de/i2/comics/index.html)

## Building models

The models that we use for benchmarks can be found in the directories
dtmc_benchmarks and mdp_benchmarks.
They have been constructed by running the gen_model_files.sh script.

## Computing Farkas certificates
The files DTMC.py, DTMC_gurobi.py, MDP.py, MDP_gurobi.py implement both
heuristic and exact subsystem computations.

## Benchmarking

Functions to run benchmark instances can be found in benchmarking.py.
Benchmarking results can be found in benchmark_runs.
Functions to plot results are implemented in plotting.py, and examples of
notebooks containing plots can be found in benchmarks/plot.ipynb and
benchmark/experiments/experiments.ipynb
