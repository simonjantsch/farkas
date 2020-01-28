import os.path
import os

import sys

from benchmarking import *

root_path="./"
if len(sys.argv) > 1:
    root_path = sys.argv[1]

csv_root= "./csv/"
heur_iter_max = 5

for i in [3,4,5,6,8]:
    for j in [2,3,4,5,6,8]:
        csv_file_path = csv_root + "leader-" + str(i) + "-" + str(j) + ".csv"

        model_path = root_path + "dtmc_benchmarks/leader_files/leader-" + str(i) + "-" + str(j)

        if not os.path.isfile(model_path + ".tra"):
            continue

        N,P,initial,to_target = dtmc.load_model(model_path,"elected")

        write_header(csv_file_path,N)

        opt = np.ones(N)
        thr = 0.1
        feasible = True

        while feasible and thr <= 1:
            subsys_path = root_path + "subsys/leader/leader-" + str(i) + "-" + str(j) + "-subsys-" + str(thr)
            feasible = run_instance_dtmc(csv_file_path,subsys_path,N,P,initial,to_target,opt,thr,heur_iter_max)
            if feasible:
                run_comics(model_path,csv_file_path,thr)
                thr += 0.2
