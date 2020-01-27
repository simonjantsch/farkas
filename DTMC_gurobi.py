from scipy.sparse import dok_matrix,hstack,vstack
from gurobipy import *
from GurobiPython import *
from helpers import *

from memory_profiler import profile

timeout = 10*60

## construct gurobi model and run lp
## returns feas, vec
## where feas=True signifies that a solution has been found
## and vec contains the solution vector

@profile
def run_gurobi(c,A_ub,rhs,find_optimum=False,rhs_multiplier=1):
    m = GurobiModel(c,A_ub,rhs)
    m2 = m.construct()
    m2.Params.NumericFocus = 3
    m2.setParam('TimeLimit', timeout)
    m2.setParam('IntFeasTol', 1e-9)
    m2.setParam('FeasibilityTol', 1e-9)
    m2.setParam('MIPGap',0)
    m2.setParam('MIPGapAbs',0)
    m2.update()
    current_vars = m2.getVars()

    if(find_optimum):
        m2.setParam('Quad',1)
        i = m2.addVars(1,[var.getAttr("VarName") for var in current_vars],name="i",vtype=GRB.BINARY,obj=c)
        m2.update()
        new_obj = LinExpr(0)
        for var in current_vars:
            rhs = LinExpr(rhs_multiplier * i[0,var.getAttr("VarName")])
            m2.addConstr(var,sense="<=",rhs=rhs)
            new_obj.add(i[0,var.getAttr("VarName")])
        m2.setObjective(new_obj, GRB.MINIMIZE)

    m2.write("model.lp")
    m2.printStats()

    m2.optimize()

    # save result into vector
    res_vec = np.zeros(len(current_vars))
    result = GurobiResult()

    if m2.status == 3:
        result.feasible = False
        return result,res_vec
    if m2.status == 9:
        result.timeout = True
    if m2.status == 2 or ((m2.status == 9) and (m2.SolCount > 0)):
        result.solution = True
        result.feasible = True
        result.obj_val = m2.getAttr("ObjVal")
        result.lower_bound = m2.ObjBound
        j = 0
        for v in current_vars:
            # if find_optimum is true, res_vec should be > 0 only if the indicator in i is 1 for the corr. entry
            if not find_optimum or (i[0,v.getAttr("VarName")].x == 1):
                res_vec[j] = v.x
            else:
                res_vec[j] = 0
            j = j+1

    return result,res_vec

# Pr(s_0) ≥ thr?
##
## min opt*y. y(I-P) ≤ d_s0 AND yb ≥ thr

def runlp_y_lb(N,initial,P,to_target,opt,thr,minimal):
    I = dok_matrix((N,N))
    I.setdiag(1)

    b_ub = to_target.reshape(N,1)

    delta = np.zeros(N)
    delta[initial] = 1

    A_ub = hstack((I-P,-b_ub)).T

    rhs = delta.copy()
    rhs.resize(N+1)

    K = 1
    if(minimal):
        max_opt = np.ones(N)
        rhs[N] = 0
        gr_res,res_vec = run_gurobi(-max_opt,A_ub,rhs,False)
        K = -gr_res.obj_val

    rhs[N] = -thr
    return run_gurobi(opt,A_ub,rhs,minimal,K)

# Pr(s_0) ≥ thr?
##
## min opt*z. (I-P)z ≤ b AND z(s_0) ≥ thr

def runlp_z_lb(N,initial,P,to_target,opt,thr,minimal):
    I = dok_matrix((N,N))
    I.setdiag(1)

    rhs = to_target.copy()
    rhs.resize(N+1)
    rhs[N] = -thr

    delta = np.zeros(N)
    delta[initial] = 1

    A_ub = vstack((I-P,-delta))
 
    return run_gurobi(opt,A_ub,rhs,minimal,1)

## iterate minimization K times using update x -> 1/x on 
## optimization function
##

def iterate_min_y(N,initial,P,to_target,opt,thr,K):
    for i in range(0,K):
        gurobi_result, res = runlp_y_lb(N,initial,P,to_target,opt,thr,minimal=False)
        if gurobi_result.feasible == True:
            opt = np.array(list(map(lambda y : 1e7 if y == 0 else 1 / y,res)))
            number_of_states = len(list(filter(lambda x: x > 0, res)))
            print("\nsubsystem size:" + str(number_of_states))
            print("\nprobability: " + str(res.dot(to_target)))
        else:
            break
    return gurobi_result,res


## iterate minimization K times using update x -> 1/x on 
## optimization function
##

def iterate_min_z(N,initial,P,to_target,opt,thr,K):
    for i in range(0,K):
        gurobi_result,res = runlp_z_lb(N,initial,P,to_target,opt,thr,minimal=False)
        if gurobi_result.feasible == True:
            opt = np.array(list(map(lambda y : 1e7 if y == 0 else 1 / y,res)))
            print(opt[initial])
            number_of_states = len(list(filter(lambda x: x > 0, res)))/2
            print("\nsubsystem size:" + str(number_of_states))
            print("\nprobability: " + str(res[initial]))
        else:
            break
    return gurobi_result,res


def compute_minimal_z(N,initial,P,to_target,opt,thr):
    return runlp_z_lb(N,initial,P,to_target,opt,thr,minimal=True)


def compute_minimal_y(N,initial,P,to_target,opt,thr):
    return runlp_y_lb(N,initial,P,to_target,opt,thr,minimal=True)

