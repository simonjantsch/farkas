import os.path
import os

import sys

from benchmarking import *

root_path="./"
if len(sys.argv) > 1:
    root_path = sys.argv[1]

csv_root= "./csv/"

heur_iter_max = 5
exact = True

for i in [512,1024,2048]:
    for j in [2]:
        if (i > 512):
            exact = False
        csv_file_path = csv_root + "brp-" + str(i) + "-" + str(j) + ".csv"

        model_path = root_path + "dtmc_benchmarks/brp_files/brp-" + str(i) + "-" + str(j)

        if not os.path.isfile(model_path + ".tra"):
            continue

        N,P,initial,to_target = dtmc.load_model(model_path,"uncertain")

        write_header(csv_file_path,N)

        opt = np.ones(N)
        thr = 5e-6
        feasible = True

        while feasible and thr <= 1:
            subsys_path = root_path + "subsys/brp/brp-" + str(i) + "-" + str(j) + "-subsys-" + str(thr)
            feasible = run_instance_dtmc(csv_file_path,subsys_path,N,P,initial,to_target,opt,thr,heur_iter_max,exact)
            if feasible:
                run_comics(model_path,csv_file_path,thr)
                thr += 1e-6
