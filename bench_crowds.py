import os.path
import os

import sys

from benchmarking import *

root_path="./"
if len(sys.argv) > 0:
    root_path = sys.argv[1]

csv_root= "./csv/"
comics_conf_file_path = "comics.conf"
heur_iter_max = 5

for i in [2,3,4,5]:
    for j in [3,4,5,6,7,8]:
        csv_file_path = csv_root + "crowds-" + str(i) + "-" + str(j) + ".csv"

        model_path = root_path + "dtmc_benchmarks/crowds_files/crowds-" + str(i) + "-" + str(j)

        if not os.path.isfile(model_path + ".tra"):
            continue

        N,P,initial,to_target = dtmc.load_model(model_path,"bad")

        write_header(csv_file_path,N)

        opt = np.ones(N)
        thr = 0.01
        feasible = True

        while feasible and thr <= 1:
            subsys_path = root_path + "subsys/crowds/crowds-" + str(i) + "-" + str(j) + "-subsys-" + str(thr)
            feasible = run_instance_dtmc(csv_file_path,subsys_path,N,P,initial,to_target,opt,thr,heur_iter_max)
            if feasible:
                run_comics(model_path,csv_file_path,thr)
                thr += 0.01
