import os.path
import re
import subprocess
import tempfile

timeout=10*60

def prism_path():
    return "/Users/simon/devel/prism-farkas/prism/bin/prism"

def result_regexp():
    return re.compile("Result: ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")

def write_prop_file(prop_file,prop):
    prop_file.write(prop)

def run_prism(model_path,prop,modeltype="-mdp"):
    prop_file = tempfile.NamedTemporaryFile()
    with open(prop_file.name,"w") as f:
        write_prop_file(f,prop)
    prism_call = [prism_path(),"-e", "1e-9","-importmodel",model_path + ".tra,lab",modeltype,prop_file.name]
    try:
        prism_out = subprocess.check_output(prism_call,timeout=timeout)
    except subprocess.TimeoutExpired:
        print("Prism could not compute probability within given time!")
        return None
    except subprocess.CalledProcessError as e:
        print("Prism returned an error!")
        print(e.output)
        return None
    else:
        prism_out_string = prism_out.decode("utf-8")
        print(prism_out_string)
        match = re.search(result_regexp(),prism_out_string)
        if match:
            return float(match.group(1))

def compute_prob_dtmc(model_path):
    return run_prism(model_path,"\"reach_min\": P=? [F \"target\"];","-dtmc")

def compute_prmin(model_path):
    return run_prism(model_path,"\"reach_min\": Pmin=? [F \"target\"];","-mdp")

def compute_prmax(model_path):
    return run_prism(model_path,"\"reach_min\": Pmax=? [F \"target\"];","-mdp")

def prism_check_precondition(model_path):
    return run_prism(model_path,"\"precond\": Pmin=? [F (\"target\" | \"fail\") ];","-mdp")

