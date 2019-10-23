from scipy.sparse import dok_matrix
import numpy as np
from helpers import *

def get_row_index(A,source,action):
    return (source*A)+action

def get_index(A,source,dest,action):
    return get_row_index(A,source,action),dest

def get_state(A,index):
    return index // A

def get_action(A,index):
    return index % A

def action_count(tra_file_path):
    action_set = set()
    with open(tra_file_path) as tra_file:
        for line in tra_file:
            line_split = line.split()
            if len(line_split) == 3:
                continue
            else:
                action_set.add(int(line_split[1]))
    return len(action_set)

def parse_mdp_matrix(tra_file_path,target_states):
    P = dok_matrix((1,1))
    N = 0
    A = action_count(tra_file_path)
    enabled_actions = dict([])
    with open(tra_file_path) as tra_file:
        for line in tra_file:
            line_split = line.split()
            # check for first lines, which has format "#states #transitions"
            if len(line_split) == 3:
                N = int(line_split[0])
                P.resize((N*A,N))
            # all other lines have format "from to prob"
            else:
                source = int(line_split[0])
                action = int(line_split[1])
                dest = int(line_split[2])
                prob = float(line_split[3])
                #if not source in target_states:
                P[get_index(A,source,dest,action)] = prob
                if source not in enabled_actions:
                    enabled_actions[source] = set([])
                enabled_actions[source].add(action)
    return N,A,P,enabled_actions


def backwards_reachable(P,states,A):
    reaching_states = states.copy()
    while True:
        current_size = len(reaching_states)
        for (source,dest) in P.keys():
            #this assumes that only pairs (s,d) appear in P.keys() where the corr. prob. is > 0
            if dest in reaching_states:
                reaching_states.add(get_state(A,source))
        if len(reaching_states) == current_size:
            break
    return reaching_states


def forwards_reachable(P,states,A):
    reachable = states.copy()
    while True:
        current_size = len(reachable)
        for (source,dest) in P.keys():
            #this assumes that only pairs (s,d) appear in P.keys() where the corr. prob. is > 0
            if get_state(A,source) in reachable:
                reachable.add(dest)
        if len(reachable) == current_size:
            break
    return reachable


def compute_fail_states(P,A,N,reaching_target):
    fail_states = set([])
    to_fail = np.zeros(A*N)
    P_tmp = dok_matrix((A*N,N))
    for (source,dest) in P.keys():
        if get_state(A,source) in reaching_target:
            if dest in reaching_target:
                P_tmp[source,dest] = P[source,dest]
            else:
                to_fail[source] += P[source,dest]
        else:
            fail_states.add(get_state(A,source))
    return P_tmp,fail_states,to_fail


def restrict_to_reachable(P_old,reachable,target_states,to_fail_old,A,enabled_actions_old):
    P = P_old.copy()
    to_fail = to_fail_old.copy()
    enabled_actions = dict([])
    #N = len(reachable.difference(target_states))
    N = len(reachable)

    to_fail.resize(A*N)
    to_target = np.zeros(A*N)

    P.clear()
    P.resize(A*N,N)
    old_to_new = dict([])
    new_iterator = 0

    #to_target_states = dict([])

    for old in reachable:
        #if old not in target_states:
        old_to_new[old] = new_iterator
        new_state_id = new_iterator
        enabled_actions[new_state_id] = enabled_actions_old[old]
        for a in range(0,A):
            new_row_index = get_row_index(A,new_state_id,a)
            old_row_index = get_row_index(A,old,a)
            to_fail[new_row_index] = to_fail_old[old_row_index]
        new_iterator = new_iterator + 1

    for (source,dest) in P_old.keys():
        old_state = get_state(A,source)
        #if (old_state in reachable.difference(target_states)):
        if (old_state in reachable):
            new_state = old_to_new[old_state]
            action = get_action(A,source)
            new_row_index = get_row_index(A,new_state,action)
            #if (dest in target_states):
            if (old_state in target_states):
                to_target[new_row_index] += 1 #P_old[source,dest]
#                if new_row_index not in to_target_states:
#                    to_target_states[new_row_index] = set()
#                to_target_states[new_row_index].add(dest)
            elif (dest in reachable):
                P[new_row_index,old_to_new[dest]] = P_old[source,dest]

    return P,to_target,to_fail,old_to_new,enabled_actions


def load_model(filepath,target):
    tra_file_path = filepath + ".tra"
    states_file_path = filepath + ".sta"
    label_file_path = filepath + ".lab"

    target_states = states_by_label(label_file_path,target)
    N,A,P,enabled_actions = parse_mdp_matrix(tra_file_path,target_states)

    reaching_target = backwards_reachable(P,target_states,A)

    P,fail_states,to_fail = compute_fail_states(P,A,N,reaching_target)

    init = get_init(label_file_path)

    reachable = forwards_reachable(P,set([init]),A)
    #N = len(reachable.difference(target_states))
    N = len(reachable)

    P,to_target,to_fail,old_to_new,enabled_actions = restrict_to_reachable(P,reachable,target_states,to_fail,A,enabled_actions)

    return N,A,P,old_to_new[init],to_target,enabled_actions


def number_of_choices(A,P):
    choice_index = dict()
    choices_per_state = dict()
    for (source,dest) in P.keys():
        source_state = get_state(A,source)
        action = get_action(A,source)
        if(source_state not in choices_per_state):
            choices_per_state[source_state] = 0
        if (source_state,action) not in choice_index:
            choice_index[(source_state,action)] = choices_per_state[source_state]
            choices_per_state[source_state] += 1
        # if(source_state not in choices_per_state):
        #     choices_per_state[source_state] = set([])
        # action = get_action(A,source)
        # choices_per_state[source_state].add(action)
    choices = 0
    for cps in choices_per_state.values():
        choices += cps
    return choices, choice_index

def print_mdp(A,P,initial,target_state,fail_state,path):
    tra_path = path + ".tra"
    lab_path = path + ".lab"

    (k,n) = P.shape
    total_choices, choice_index = number_of_choices(A,P)

    with open(tra_path, "w") as tra_file:
        tra_file.write(str(n) + " " + str(total_choices) + " " + str(P.nnz) + "\n")
        for (source,dest) in P.keys():
            state = get_state(A,source)
            action = get_action(A,source)
            tra_file.write(str(state) + " " + str(choice_index[state,action]) + " " + str(dest) + " " + str(P[source,dest]) +"\n")
    with open(lab_path, "w") as lab_file:
        lab_file.write("0=\"init\" 1=\"target\" 2=\"fail\"\n")
        lab_file.write(str(initial) + ": 0\n")
        lab_file.write(str(target_state) + ": 1\n")
        lab_file.write(str(fail_state) + ": 2\n")

