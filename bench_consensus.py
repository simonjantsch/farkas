import os.path
import os

import sys

from benchmarking import *

root_path="./"
if len(sys.argv) > 0:
    root_path = sys.argv[1]

csv_root= "./csv/"
heur_iter_max = 5

precondition_satisfied = True
for i in [2,4]:
    if not precondition_satisfied:
        break
    for j in [2,4]:
        csv_file_path = csv_root + "consensus-" + str(i) + "-" + str(j) + ".csv"

        model_path = root_path + "mdp_benchmarks/consensus_files/consensus-" + str(i) + "-" + str(j)
        N,A,P,initial,to_target,enabled_actions = mdp.load_model(model_path,"finished")

        if not check_precondition(N,A,P,initial,to_target,enabled_actions):
            print("Warning: precondition not satisfied!")
            precondition_satisfied = False
            break

        write_header(csv_file_path,N)

        opt_prmax = np.ones(A*N)
        opt_prmin = np.ones(N)
        thr = 0.1
        feasible = True

        while feasible and thr <= 1:
            subsys_path_prmax = root_path + "subsys/consensus/consensus-prmax-" + str(i) + "-" + str(j) + "-subsys-" + str(thr)
            feasible = run_instance_mdp_prmax(csv_file_path,subsys_path_prmax,N,A,P,initial,to_target,opt_prmax,thr,enabled_actions,heur_iter_max)
            if feasible:
                run_ltlsubsys_min_prmax(csv_file_path,subsys_path_prmax,N,A,P,initial,to_target,opt_prmax,thr,enabled_actions)
            thr += 0.2

        feasible = True
        thr = 0.1
        while feasible and thr <= 1:
            subsys_path_prmin = root_path + "subsys/consensus/consensus-prmin-" + str(i) + "-" + str(j) + "-subsys-" + str(thr)
            feasible = run_instance_mdp_prmin(csv_file_path,subsys_path_prmin,N,A,P,initial,to_target,opt_prmin,thr,enabled_actions,heur_iter_max)
            thr += 0.2
