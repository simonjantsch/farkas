import re
from dataclasses import dataclass

def states_by_label(label_file_path,label):
    state_set = set()
    mark_regexp = re.compile("([0-9]+)=\"" + label + "\"")
    line_regexp = re.compile("([0-9]+):([\W,0-9]+)")
    with open(label_file_path) as label_file:
        first_line = True
        for line in label_file:
            if first_line:
                regexp_res = mark_regexp.search(line)
                mark = int(regexp_res.group(1))
                first_line = False
            else:
                regexp_res = line_regexp.search(line)
                state_labels = regexp_res.group(2).split()
                if mark in list(map(int,state_labels)):
                    state_set.add(int(regexp_res.group(1)))
    return state_set

def get_init(label_file_path):
    init_states = states_by_label(label_file_path,"init")

    if len(init_states) > 1:
        print("error: more then one init state found!")
    if len(init_states) == 0:
        print("error: no init state found")

    init = init_states.pop()
    return init

class ParseError(Exception):
    pass

@dataclass
class GurobiResult:
    feasible: bool = None
    solution: bool = False
    timeout: bool = False
    interrupted: bool = False
    unbounded: bool = False
    obj_val: float = 0
    lower_bound: float = 0

