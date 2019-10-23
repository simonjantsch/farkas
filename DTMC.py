import numpy as np
import re
from scipy.sparse import dok_matrix
from helpers import *

def parse_matrix(tra_file_path,target_states):
    P = dok_matrix((1,1))
    N = 0
    with open(tra_file_path) as tra_file:
        for line in tra_file:
            line_split = line.split()
            # check for first lines, which has format "#states #transitions"
            if len(line_split) == 2:
                N = int(line_split[0])
                P.resize((N,N))
            # all other lines have format "from to prob"
            else:
                source = int(line_split[0])
                dest = int(line_split[1])
                prob = float(line_split[2])
                P[source,dest] = prob
    return N,P

def backwards_reachable(P,states):
    reaching_states = states.copy()
    while True:
        current_size = len(reaching_states)
        for (source,dest) in P.keys():
            #this assumes that only pairs (s,d) appear in P.keys() where the corr. prob. is > 0
            if dest in reaching_states:
                reaching_states.add(source)
        if len(reaching_states) == current_size:
            break
    return reaching_states

def forwards_reachable(P,states):
    reachable = states.copy()
    while True:
        current_size = len(reachable)
        for (source,dest) in P.keys():
            #this assumes that only pairs (s,d) appear in P.keys() where the corr. prob. is > 0
            if source in reachable:
                reachable.add(dest)
        if len(reachable) == current_size:
            break
    return reachable

def compute_fail_states(P,N,reaching_target):
    fail_states = set([])
    to_fail = np.zeros(N)
    P_tmp = dok_matrix((N,N))
    for (source,dest) in P.keys():
        if source in reaching_target:
            if dest in reaching_target:
                P_tmp[source,dest] = P[source,dest]
            else:
                to_fail[source] += P[source,dest]
        else:
            fail_states.add(source)
    return P_tmp,fail_states,to_fail

def restrict_to_reachable(P_old,reachable,target_states,to_fail_old):
    P = P_old.copy()
    to_fail = to_fail_old.copy()
    N = len(reachable)

    to_fail.resize(N)
    to_target = np.zeros(N)

    P.clear()
    P.resize(N,N)
    old_to_new = dict([])
    new_iterator = 0

    for old in reachable:
        old_to_new[old] = new_iterator
        to_fail[new_iterator] = to_fail_old[old]
        new_iterator = new_iterator + 1

    for state in target_states:
        to_target[old_to_new[state]] = 1

    for (source,dest) in P_old.keys():
        if (source in reachable.difference(target_states)) and (dest in reachable):
            P[old_to_new[source],old_to_new[dest]] = P_old[source,dest]
    return P,to_target,to_fail,old_to_new

def load_model(filepath,target):
    tra_file_path = filepath + ".tra"
    states_file_path = filepath + ".sta"
    label_file_path = filepath + ".lab"

    target_states = states_by_label(label_file_path,target)
#    print(target_states)

    N,P = parse_matrix(tra_file_path,target_states)

    reaching_target = backwards_reachable(P,target_states)
#    print(reaching_target)

    P,fail_states,to_fail = compute_fail_states(P,N,reaching_target)

    init = get_init(label_file_path)

    reachable = forwards_reachable(P,set([init]))
#    print(reachable)
    N = len(reachable)

    P,to_target,to_fail,old_to_new = restrict_to_reachable(P,reachable,target_states,to_fail)
#    print(to_target)

    return N,P,old_to_new[init],to_target

def print_dtmc(P,initial,target,path):
    tra_path = path + ".tra"
    lab_path = path + ".lab"
    (n,n) = P.shape
    with open(tra_path, "w") as tra_file:
        tra_file.write(str(n) + " " + str(P.nnz) + "\n")
        for (source,dest) in P.keys():
            tra_file.write(str(source) + " " + str(dest) + " " + str(P[source,dest]) + "\n")
    with open(lab_path, "w") as lab_file:
        lab_file.write("0=\"init\" 1=\"target\"\n")
        lab_file.write(str(initial) + ": 0\n")
        lab_file.write(str(target) + ": 1\n")

def prism_to_comics(tra_path,lab_path,target_label,dest_path):
    init = get_init(lab_path)
    target_states = states_by_label(lab_path,target_label)
    with open(tra_path) as tra_file:
        with open(dest_path,"w") as dest_file:
            for line in tra_file:
                line_split = line.split()
                # check for first lines, which has format "#states #transitions"
                if len(line_split) == 2:
                    N = int(line_split[0])
                    T = int(line_split[1])
                    dest_file.write("STATES " + str(N) + "\n")
                    dest_file.write("TRANSITIONS " + str(N) + "\n")
                    dest_file.write("INITIAL " + str(init) + "\n")
                    for s in target_states:
                        dest_file.write("TARGET " + str(s) + "\n")
                # all other lines have format "from to prob"
                else:
                    dest_file.write(line)
