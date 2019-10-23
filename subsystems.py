#import nbimporter
import MDP as mdp
import DTMC as dtmc
import numpy as np
from scipy.sparse import dok_matrix

def get_subsys_dtmc(res):
    subsys_states = set()
    for i in range(0,len(res)):
        if res[i] > 0:
            subsys_states.add(i)
            i += 1
    subsys_size = len(subsys_states)
    return subsys_states,subsys_size

def export_dtmc_subsystem(P,initial,to_target,subsystem_states,path):
    N_sub = len(subsystem_states)
    state_mapping = dict([])
    i = 0
    for state in subsystem_states:
        state_mapping[state] = i
        i = i + 1
    P_sub = dok_matrix((N_sub+2,N_sub+2))
    target_state = N_sub
    fail_state = N_sub+1
    in_subsys = dict([])
    for (source,dest) in P.keys():
        if (source in subsystem_states) and (dest in subsystem_states):
            P_sub[state_mapping[source],state_mapping[dest]] = P[source,dest]
            if source not in in_subsys.keys():
                in_subsys[source] = 0
            in_subsys[source] += P[source,dest]
    for state in subsystem_states:
        P_sub[state_mapping[state],target_state] = to_target[state]
        if state not in in_subsys.keys():
            in_subsys[state] = 0
        P_sub[state_mapping[state],fail_state] = 1 - (to_target[state] + in_subsys[state])
    P_sub[target_state,target_state] = 1
    P_sub[fail_state,fail_state] = 1

    dtmc.print_dtmc(P_sub,state_mapping[initial],target_state,path)

def get_subsys_from_y(res,A):
    subsys_actions = set()
    for i in range(0,len(res)):
        if res[i] > 0:
            subsys_actions.add((mdp.get_state(A,i),mdp.get_action(A,i)))
    subsys_states = set([s for (s,a) in subsys_actions])
    subsys_size = len(subsys_states)
    return subsys_states,subsys_actions,subsys_size

def get_subsys_from_z(res,A,enabled):
    subsys_states = set()
    for i in range(0,len(res)):
        if res[i] > 0:
            subsys_states.add(i)
            for a in enabled[i]:
                row = mdp.get_row_index(A,i,a)
    subsys_actions = set([(s,a) for s in subsys_states for a in enabled[s]])
    subsys_size = len(subsys_states)
    return subsys_states,subsys_actions,subsys_size

def export_mdp_subsystem(N,A,P,initial,to_target,subsys_states,subsys_actions,path):
    N_sub = len(subsys_states)
    state_mapping = dict([])
    i = 0
    for state in subsys_states:
        state_mapping[state] = i
        i = i + 1
    P_sub = dok_matrix((A*(N_sub+2),N_sub+2))
    target_state = N_sub
    fail_state = N_sub+1
    in_subsys= dict([])

    for (source,dest) in P.keys():
        state = mdp.get_state(A,source)
        action = mdp.get_action(A,source)
        if ((state,action) in subsys_actions) and (dest in subsys_states):
            new_index = mdp.get_index(A,state_mapping[state],state_mapping[dest],action)
            P_sub[new_index] = P[source,dest]
            if (state,action) not in in_subsys.keys():
                in_subsys[(state,action)] = 0
            in_subsys[(state,action)] += P[source,dest]

    for (state,action) in subsys_actions:
        new_state = state_mapping[state]
        state_action_index = mdp.get_row_index(A,state,action)
        to_target_val = to_target[state_action_index]
        P_sub[mdp.get_index(A,new_state,target_state,action)] = to_target_val
        if (state,action) not in in_subsys.keys():
            in_subsys[(state,action)] = 0
        P_sub[mdp.get_index(A,new_state,fail_state,action)] = 1 - (to_target_val + in_subsys[(state,action)])
    mdp.print_mdp(A,P_sub,state_mapping[initial],target_state,fail_state,path)

