import numpy as np
import os.path
import os
import tempfile
from ttictoc import TicToc

#import nbimporter
import MDP as mdp
import MDP_gurobi as mdp_gurobi
import DTMC as dtmc
import DTMC_gurobi as dtmc_gurobi
import comics_tools as comics
from helpers import *
from prism import *
from subsystems import *

timeout = 30*60
comics_path="/home/jantsch/comics-1.0/comics"
error_log_file="error.log"

def write_header(csv_file_path,N):
    with open(csv_file_path,"w") as csv_file:
        csv_file.write("tool,mode,threshold,t_wall,t_cpu,timeout,mc time,states,lower_bound,trans,prob,prob LP,heur_iter,info (total states:" + str(N) + ")\n")

def l(something):
    if something == None:
        return "-"
    else:
        return str(something)

def write_line(csv_file_path,tool=None,mode=None,thr=None,t_wall=None,t_cpu=None,timeout=None,mc_time=None,states=None,lower_bound=None,trans=None,prob=None,prob_lp=None,info=None,heur_iter=None):
    with open(csv_file_path,"a") as csv_file:
        csv_file.write(l(tool) + "," + l(mode) + "," + l(thr) + "," + l(t_wall) + "," + l(t_cpu) + "," + l(timeout) + "," + l(mc_time) + "," + l(states) + "," + l(lower_bound) + "," + l(trans) + "," + l(prob) + "," + l(prob_lp) + "," + l(heur_iter) + "," + l(info) + "\n")


def handle_fark_res_y(P,initial,to_target,subsys_path,csv_file_path,thr,mode,gurobi_res,res_vec,t_wall,t_cpu,heur_iter,exact=False):
    if gurobi_res.feasible == False:
        return False

    if gurobi_res.solution == False:
        write_line(csv_file_path,tool="fark",mode=mode,thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gurobi_res.timeout,lower_bound=lower_bound,heur_iter=heur_iter)
        return None

    subsys_states,size = get_subsys_dtmc(res_vec)
    export_dtmc_subsystem(P,initial,to_target,subsys_states,subsys_path)
    subsys_prob_prism = compute_prob_dtmc(subsys_path)
    prob = res_vec.dot(to_target)

    lower_bound = None
    if exact:
        lower_bound = gurobi_res.lower_bound

    write_line(csv_file_path,tool="fark",mode=mode,thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gurobi_res.timeout,states=size,lower_bound=lower_bound,prob=subsys_prob_prism,prob_lp=prob,heur_iter=heur_iter)
    return True

def handle_fark_res_z(P,initial,to_target,subsys_path,csv_file_path,thr,mode,gurobi_res,res_vec,t_wall,t_cpu,heur_iter,exact=False):
    if gurobi_res.feasible == False:
        return False

    if gurobi_res.solution == False:
        write_line(csv_file_path,tool="fark",mode=mode,thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gurobi_res.timeout,lower_bound=lower_bound,heur_iter=heur_iter)
        return None

    subsys_states,size = get_subsys_dtmc(res_vec)
    export_dtmc_subsystem(P,initial,to_target,subsys_states,subsys_path)
    subsys_prob_prism = compute_prob_dtmc(subsys_path)
    prob = res_vec[initial]

    lower_bound = None
    if exact:
        lower_bound=gurobi_res.lower_bound

    write_line(csv_file_path,tool="fark",mode=mode,thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gurobi_res.timeout,states=size,lower_bound=lower_bound,prob=subsys_prob_prism,prob_lp=prob,heur_iter=heur_iter)
    return True

def run_instance_dtmc(csv_file_path,subsys_path,N,P,initial,to_target,opt,thr,heur_iter_max):

    t_wall = TicToc()
    t_cpu = TicToc(method='process_time')

    ## compute small witnesses using heuristics, for iterations up to heur_iter_max

    for heur_iter in range(1,heur_iter_max+1):
        ## compute and write csv line for y_form heuristic

        t_wall.tic()
        t_cpu.tic()
        gr_y,res_y = dtmc_gurobi.iterate_min_y(N,initial,P,to_target,opt,thr,heur_iter)
        t_wall.toc()
        t_cpu.toc()

        feasible = handle_fark_res_y(P,initial,to_target,subsys_path,csv_file_path,thr,"y form",gr_y,res_y,t_wall,t_cpu,heur_iter)

        if feasible == False:
            return False

        ## compute and write csv line for z_form heuristic
        t_wall.tic()
        t_cpu.tic()
        gr_z,res_z = dtmc_gurobi.iterate_min_z(N,initial,P,to_target,opt,thr,heur_iter)
        t_wall.toc()
        t_cpu.toc()

        feasible = handle_fark_res_z(P,initial,to_target,subsys_path,csv_file_path,thr,"z form",gr_z,res_z,t_wall,t_cpu,heur_iter)
        if feasible == False:
            return False

    ## compute minimal witnesses

    ## compute and write csv line for y_form exact
    t_wall.tic()
    t_cpu.tic()
    gr_y_ex,res_y_ex = dtmc_gurobi.compute_minimal_y(N,initial,P,to_target,opt,thr)
    t_wall.toc()
    t_cpu.toc()

    feasible = handle_fark_res_y(P,initial,to_target,subsys_path,csv_file_path,thr,"y exact",gr_y_ex,res_y_ex,t_wall,t_cpu,None,exact=True)

    if feasible == False:
        return False

    ## compute and write csv line for z_form exact
    t_wall.tic()
    t_cpu.tic()
    gr_z_ex,res_z_ex = dtmc_gurobi.compute_minimal_z(N,initial,P,to_target,opt,thr)
    t_wall.toc()
    t_cpu.toc()

    feasible = handle_fark_res_z(P,initial,to_target,subsys_path,csv_file_path,thr,"z exact",gr_z_ex,res_z_ex,t_wall,t_cpu,None,exact=True)
    if feasible == False:
        return False

    return True

def run_instance_mdp_prmax(csv_file_path,subsys_file_path,N,A,P,initial,to_target,opt,thr,enabled_actions,heur_iter_max):
    t_wall = TicToc()
    t_cpu = TicToc(method='process_time')

    for heur_iter in range(1,heur_iter_max+1):

        t_wall.tic()
        t_cpu.tic()
        gr_res,res = mdp_gurobi.iterate_prmax(N,A,initial,P,to_target,opt,thr,heur_iter,enabled_actions)
        t_wall.toc()
        t_cpu.toc()
        if gr_res.feasible == False:
            return False

        if gr_res.solution == False:
            write_line(csv_file_path,tool="fark",mode="prax",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,heur_iter=heur_iter)
            continue

        subsys_states,subsys_actions,size = get_subsys_from_y(res,A)
        export_mdp_subsystem(N,A,P,initial,to_target,subsys_states,subsys_actions,subsys_file_path)
        prism_prob = compute_prmax(subsys_file_path)
        prob = res.dot(to_target)
        write_line(csv_file_path,tool="fark",mode="prmax",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,states=size,prob=prism_prob,prob_lp=prob,heur_iter=heur_iter)

    ## compute a minimal subsystem
    t_wall.tic()
    t_cpu.toc()
    gr_res_opt,res_opt = mdp_gurobi.compute_minimal_prmax(N,A,initial,P,to_target,thr,enabled_actions)
    t_wall.toc()
    t_cpu.toc()
    if gr_res_opt.solution == False:
        write_line(csv_file_path,tool="fark",mode="prmax exact",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res_opt.timeout,lower_bound=gr_res_opt.lower_bound)
        return True
    subsys_states_opt,subsys_actions_opt,size_opt = get_subsys_from_y(res_opt,A)
    export_mdp_subsystem(N,A,P,initial,to_target,subsys_states_opt,subsys_actions_opt,subsys_file_path)
    prism_prob_opt = compute_prmax(subsys_file_path)
    prob_opt = res_opt.dot(to_target)
    write_line(csv_file_path,tool="fark",mode="prmax exact",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res_opt.timeout,states=gr_res_opt.obj_val,lower_bound=gr_res_opt.lower_bound,prob=prism_prob_opt,prob_lp=prob_opt)
    return True

def run_instance_mdp_prmin(csv_file_path,subsys_file_path,N,A,P,initial,to_target,opt,thr,enabled_actions,heur_iter_max):
    t_wall = TicToc()
    t_cpu = TicToc(method='process_time')

    for heur_iter in range(1,heur_iter_max+1):
        t_wall.tic()
        t_cpu.tic()
        gr_res,res = mdp_gurobi.iterate_prmin(N,A,initial,P,to_target,opt,thr,heur_iter,enabled_actions)
        t_wall.toc()
        t_cpu.toc()
        if gr_res.feasible == False:
            return False

        if gr_res.solution == False:
            write_line(csv_file_path,tool="fark",mode="prmin",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,heur_iter=heur_iter)
            continue

        subsys_states,subsys_actions,size = get_subsys_from_z(res,A,enabled_actions)
        export_mdp_subsystem(N,A,P,initial,to_target,subsys_states,subsys_actions,subsys_file_path)
        prism_prob = compute_prmin(subsys_file_path)
        prob = res[initial]
        write_line(csv_file_path,tool="fark",mode="prmin",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,states=size,prob=prism_prob,prob_lp=prob,heur_iter=heur_iter)

    ## compute a minimal subsystem
    t_wall.tic()
    t_cpu.tic()
    gr_opt,res_opt = mdp_gurobi.compute_minimal_prmin(N,A,initial,P,to_target,thr,enabled_actions)
    t_wall.toc()
    t_cpu.toc()
    if gr_opt.solution == False:
        write_line(csv_file_path,tool="fark",mode="prmin exact",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_opt.timeout,lower_bound=gr_opt.lower_bound)
        return True
    subsys_states_opt,subsys_actions_opt,size_opt = get_subsys_from_z(res_opt,A,enabled_actions)
    export_mdp_subsystem(N,A,P,initial,to_target,subsys_states_opt,subsys_actions_opt,subsys_file_path)
    prism_prob_opt = compute_prmin(subsys_file_path)
    prob_opt = res_opt[initial]
    write_line(csv_file_path,tool="fark",mode="prmin exact",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_opt.timeout,states=gr_opt.obj_val,lower_bound=gr_opt.lower_bound,prob=prism_prob_opt,prob_lp=prob_opt)
    return True

def run_ltlsubsys_min_prmax(csv_file_path,subsys_file_path,N,A,P,initial,to_target,opt,thr,enabled_actions):
    t_wall = TicToc()
    t_cpu = TicToc(method='process_time')

    t_wall.tic()
    t_cpu.tic()
    gr_res,res = mdp_gurobi.compute_minimal_prmax_ltlsubsys(N,A,initial,P,to_target,thr,enabled_actions)
    t_wall.toc()
    t_cpu.toc()

    if gr_res.feasible == False:
        return False

    if gr_res.solution == False:
        write_line(csv_file_path,tool="ltlsubsys",mode="prmax exact",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,lower_bound=gr_res.lower_bound)
        return True
    subsys_states,subsys_actions,size = get_subsys_from_z(res,A,enabled_actions)
    export_mdp_subsystem(N,A,P,initial,to_target,subsys_states,subsys_actions,subsys_file_path)
    prism_prob = compute_prmax(subsys_file_path)
    prob = res[initial]
    write_line(csv_file_path,tool="ltlsubsys",mode="prmax minimal",thr=thr,t_wall=t_wall.elapsed,t_cpu=t_cpu.elapsed,timeout=gr_res.timeout,states=gr_res.obj_val,lower_bound=gr_res.lower_bound,prob=prism_prob,prob_lp=prob)

def check_precondition(N,A,P,initial,to_target,enabled_actions):
    mark_all_states = np.ones(N)
    full_sys,full_sys_actions,full_sys_size = get_subsys_from_z(mark_all_states,A,enabled_actions)
    sys_file = "system"
    export_mdp_subsystem(N,A,P,initial,to_target,full_sys,full_sys_actions,sys_file)
    res = prism_check_precondition(sys_file)
    if res < 1:
        return False
    else:
        return True

def run_comics(model_path,csv_file_path,thr):
    if not os.path.isfile(model_path + ".dtmc"):
        return

    # run comics with global search strategy
    comics_conf_file = tempfile.NamedTemporaryFile()
    rel_path_conf = os.path.relpath(comics_conf_file.name)
    comics.write_comics_conf(rel_path_conf,os.path.relpath(model_path + ".dtmc"),"global",thr)
    try:
        print((subprocess.check_output([comics_path,rel_path_conf],timeout=timeout)).decode("utf-8"))
    except subprocess.TimeoutExpired:
        write_line(csv_file_path,tool="comics",mode="global",thr=thr,timeout=True)
    except subprocess.CalledProcessError as e:
        print("Warning: comics returned with returncode" + str(e.returncode))
        print(e.output)
        with open("error.log","a") as error_file:
            error_file.write(e.output.decode("utf-8"))
        if e.returncode == 6:
            write_line(csv_file_path,tool="comics",mode="global",thr=thr,info="MEM-OUT")
        else:
            write_line(csv_file_path,tool="comics",mode="global",thr=thr,info="error")
    else:
        try:
            states,trans,orig_prob,sub_prob,mc_time,ce_time = comics.parse_comics_result("counter_example_summary.txt")
        except ParseError:
            write_line(csv_file_path,tool="comics",mode="global",thr=thr,info="parse error")
            print("Warning: comics counter_example_summary.txt could not be parsed!")
            with open("counter_example_summary.txt") as ce_file:
                with open("error.log", "a") as error_file:
                    print("Warning: comics counter_example_summary.txt could not be parsed!")
                    error_file.write("Warning: comics counter_example_summary.txt could not be parsed!")
                    for line in ce_file:
                        print(line)
                        error_file.write(line)
        else:
            write_line(csv_file_path,tool="comics",mode="global",thr=thr,t_wall=ce_time,states=states,prob=sub_prob)
            os.remove("counter_example_summary.txt")

    # run comics with local search strategy
    comics.write_comics_conf(rel_path_conf,os.path.relpath(model_path + ".dtmc"),"local",thr)
    try:
        print(rel_path_conf)
        with open(rel_path_conf) as conf_file:
            for line in conf_file:
                print(line)
        subprocess.check_output([comics_path,rel_path_conf],timeout=timeout)
    except subprocess.TimeoutExpired:
        write_line(csv_file_path,tool="comics",mode="local",thr=thr,timeout=True)
    except subprocess.CalledProcessError as e:
        print("Warning: comics returned with returncode" + str(e.returncode))
        print(e.output)
        with open("error.log","a") as error_file:
            error_file.write(e.output.decode("utf-8"))
        if e.returncode == 6:
            write_line(csv_file_path,tool="comics",mode="local",thr=thr,info="MEM-OUT")
        else:
            write_line(csv_file_path,tool="comics",mode="local",thr=thr,info="error")
    else:
        try:
            states,trans,orig_prob,sub_prob,mc_time,ce_time = comics.parse_comics_result("counter_example_summary.txt")
        except ParseError:
            write_line(csv_file_path,tool="comics",mode="local",thr=thr,info="parse error")
            print("Warning: comics counter_example_summary.txt could not be parsed!")
            with open("counter_example_summary.txt") as ce_file:
                with open("error.log","a") as error_file:
                    print("Warning: comics counter_example_summary.txt could not be parsed!")
                    error_file.write("Warning: comics counter_example_summary.txt could not be parsed!")
                    for line in ce_file:
                        print(line)
                        error_file.write(line)
        else:
            write_line(csv_file_path,tool="comics",mode="local",thr=thr,t_wall=ce_time,states=states,prob=sub_prob)
            os.remove("counter_example_summary.txt")
