#import nbimporter
import DTMC as dtmc
from helpers import *

import re
import os.path

crowds_instances = set()
for i in [2,3,4,5]:
    for j in [3,4,5,6,7,8,9,10,11,12]:
        crowds_instances.add("dtmc_benchmarks/crowds_files/crowds-" + str(i) + "-" + str(j))

leader_instances = set()
for i in [3,4,5,6,8]:
    for j in [2,3,4,5,6,8]:
        leader_instances.add("dtmc_benchmarks/leader_files/leader-" + str(i) + "-" + str(j))

brp_instances = set()
for i in [32,64,128,512,1024,2048]:
    for j in [2,3,4]:
        brp_instances.add("dtmc_benchmarks/brp_files/brp-" + str(i) + "-" + str(j))

def build_comics_models():
    for instance_set,target_label in [(crowds_instances,"bad"),(leader_instances,"elected"),(brp_instances,"uncertain")]:
        for instance in instance_set:
            tra_path = instance + ".tra"
            lab_path = instance + ".lab"
            dest_path = instance + ".dtmc"
            if os.path.isfile(tra_path) and os.path.isfile(lab_path):
                dtmc.prism_to_comics(tra_path,lab_path,target_label,dest_path)

def write_comics_conf(conf_path,dtmc_path,mode,threshold):
    with open(conf_path,"w") as conf_file:
        conf_file.write("TASK Counterexample\n")
        conf_file.write("PROBABILITY_BOUND " + str(threshold) + "\n")
        conf_file.write("DTMC_FILE " + dtmc_path + "\n")
        conf_file.write("SEARCH_ALGORITHM " + mode + "\n")
        conf_file.write("ABSTRACTION concrete\n")

def parse_comics_result(res_path):
    found_size = False
    found_origin_prob = False
    found_subsys_prob = False
    found_mc_time = False
    found_ce_time = False
    subsys_regexp = re.compile("Counter example size: ([0-9]+) states, ([0-9]+) transitions")
    orig_prob_regexp = re.compile("Model Checking result of original system: ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")
    subsys_prob_regexp = re.compile("Closure probability: ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")
    mc_time_regexp = re.compile("Time for model checking: ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?) secs")
    ce_time_regexp = re.compile("Time of counter example computation: ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?) secs")
    with open(res_path) as res_file:
        for line in res_file:
            match = re.match(subsys_regexp,line)
            if match:
                subsys_states = int(match.group(1))
                subsys_trans = int(match.group(2))
                found_size = True
                continue
            match = re.match(orig_prob_regexp,line)
            if match:
                orig_prob = float(match.group(1))
                found_origin_prob = True
                continue
            match = re.match(subsys_prob_regexp,line)
            if match:
                subsys_prob = float(match.group(1))
                found_subsys_prob = True
                continue
            match = re.match(mc_time_regexp,line)
            if match:
                mc_time = float(match.group(1))
                found_mc_time = True
                continue
            match = re.match(ce_time_regexp,line)
            if match:
                ce_time = float(match.group(1))
                found_ce_time = True
                break
    if found_size and found_origin_prob and found_subsys_prob and found_mc_time and found_ce_time:
        return subsys_states,subsys_trans,orig_prob,subsys_prob,mc_time,ce_time
    else:
        raise ParseError("couldnt parse comics result")
