from scipy.sparse import dok_matrix,hstack,vstack,identity
from gurobipy import *
from GurobiPython import *
from MDP import *
from helpers import *

from memory_profiler import profile

timeout = 30*60

## construct gurobi model and run lp
## returns feas, vec
## where feas=True signifies that a solution has been found
## and vec contains the solution vector

def callback2(model,where):
    if where == GRB.Callback.SIMPLEX:
        obj = model.cbGet(GRB.Callback.SPX_OBJVAL)
        print(obj)

def run_gurobi(c,A_ub,rhs,find_optimum=False,rhs_multiplier=1,zero_vars=None,set_binary=None):
    return run_gurobi_with_cutoff(c,A_ub,rhs,find_optimum,rhs_multiplier,callback=None,zero_vars=zero_vars,set_binary=set_binary)

@profile
def run_gurobi_with_cutoff(c,A_ub,rhs,find_optimum=False,rhs_multiplier=1,callback=None,zero_vars=None,set_binary=None):
    m = GurobiModel(c,A_ub,rhs)
    m2 = m.construct()
    m2.Params.NumericFocus = 3
    m2.setParam('TimeLimit', timeout)
    m2.setParam('IntFeasTol', 1e-9)
    m2.setParam('FeasibilityTol', 1e-9)
    m2.setParam('MIPGap',0)
    m2.setParam('MIPGapAbs',0)
    if not (callback == None):
        m2.setParam("Presolve",0)
        m2.setParam("PreDual",0)
        m2.setParam("DualReductions",0)
        m2.setParam("Method",0)
        m2.optimize(callback)
        #m2.setObjective(0)
        m2.optimize(callback2)

    m2.update()
    current_vars = m2.getVars()

    if(zero_vars):
        for x in zero_vars:
            current_vars[x].setAttr(GRB.Attr.UB,0.0)

    if(set_binary):
        for x in set_binary:
            current_vars[x].setAttr(GRB.Attr.VType,GRB.BINARY)

    if(find_optimum):
        i = m2.addVars(1,[var.getAttr("VarName") for var in current_vars],name="i",vtype=GRB.BINARY,obj=c)
        m2.update()
        new_obj = LinExpr(0)
        for var in current_vars:
            rhs = LinExpr(rhs_multiplier * i[0,var.getAttr("VarName")])
            m2.addConstr(var,sense="<=",rhs=rhs)
            new_obj.add(i[0,var.getAttr("VarName")])
        m2.setObjective(new_obj, GRB.MINIMIZE)

    m2.optimize()

    # save result into vector
    res_vec = np.zeros(len(current_vars))
    j = 0
    result = GurobiResult()

    if m2.status == 11:
        result.interrupted = True
    if m2.status == 3:
        result.feasible = False
    if m2.status == 5:
        result.unbounded = True
    if m2.status == 9:
        result.timeout = True
    if (m2.status == 2) or ((m2.status == 9) and (m2.SolCount > 0)):
        result.solution = True
        result.feasible = True
        result.obj_val = m2.getAttr("ObjVal")
        result.lower_bound = m2.ObjBound
        for v in current_vars:
            if v.getAttr("VType") == GRB.CONTINUOUS:
                if not find_optimum or (i[0,v.getAttr("VarName")].x == 1):
                    res_vec[j] = v.x
                else:
                    res_vec[j] = 0
                j = j+1

    return result, res_vec



## min opt*y. y(I-P) ≤ d_s0 AND yb ≥ thr

def runlp_y_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal):
    I = dok_matrix((A*N,N))

    not_enabled = set([])
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1
            else:
                not_enabled.add(get_row_index(A,n,k))

    b_ub = to_target.reshape(A*N,1)

    delta = np.zeros(N)
    delta[initial] = 1

    A_ub = hstack((I-P,-b_ub)).T

    rhs = delta.copy()
    rhs.resize(N+1)

    K = 1
    if(minimal):
        max_opt = np.ones(N*A)
        rhs[N] = 0
        gr,res = run_gurobi(-max_opt,A_ub,rhs,zero_vars=not_enabled)
        K = -gr.obj_val

    rhs[N] = -thr
    return run_gurobi(opt,A_ub,rhs,minimal,K)


# Pr_min(s_0) ≥ thr?
##
## min opt*z. (I-P)z ≤ b AND z(s_0) ≥ thr

def runlp_z_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    #print(I)
    rhs = to_target.copy()
    rhs.resize((A*N)+1)
    rhs[A*N] = -thr
    delta = np.zeros(N)
    delta[initial] = 1

    A_ub = vstack(((I-P),-delta))
    return run_gurobi(opt,A_ub,rhs,minimal,1)


# LP for Pr_min
#
# max z. (I-P)z ≤ b

def prmin_lp(N,A,initial,P,to_target,enabled_actions):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    rhs = to_target.copy()
    opt = np.ones(N)
    return run_gurobi(-opt,I-P,rhs)

def cutoff_callback(coeff,thr,model,where):
    if where == GRB.Callback.SIMPLEX:
        obj = model.cbGet(GRB.Callback.SPX_OBJVAL)
        print(obj)
        if (coeff*obj) >= thr:
            model.terminate()

# LP for Pr_min ≥ thr

def prmin_geq_thr(N,A,initial,P,to_target,enabled_actions,thr):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    rhs = to_target.copy()
    opt = np.zeros(N)
    opt[initial] = 1

    return run_gurobi_with_cutoff(-opt,I-P,rhs, lambda m,w: cutoff_callback(-1,thr,m,w))


# LP for Pr_max
# 
# min z. (I-P)z ≥ b

def prmax_lp(N,A,initial,P,to_target,enabled_actions):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    rhs = to_target.copy()
    opt = np.ones(N)
    return run_gurobi(opt,-(I-P),-rhs)

# LP for Pr_max ≥ thr

def prmax_geq_thr(N,A,initial,P,to_target,enabled_actions,thr):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    rhs = to_target.copy()
    opt = np.zeros(N)
    opt[initial] = 1

    return run_gurobi_with_cutoff(opt,-(I-P),-rhs,lambda m,w: cutoff_callback(1,thr,m,w))

## iterate minimization K times using update x -> 1/x on 
## optimization function
##

def iterate_prmax(N,A,initial,P,to_target,opt,thr,K,enabled_actions):
    for i in range(0,K):
        gurobi_res,res = runlp_y_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal=False)
        if gurobi_res.feasible == True:
            opt = np.array(list(map(lambda y : 1e7 if y == 0 else 1 / y,res)))
            number_of_states = len(list(filter(lambda x: x > 0, res)))
            print("\nsubsystem size:" + str(number_of_states))
            print("\nprobability: " + str(res.dot(to_target)))
        else:
            break
    return gurobi_res,res

## iterate minimization K times using update x -> 1/x on 
## optimization function
##

def iterate_prmin(N,A,initial,P,to_target,opt,thr,K,enabled_actions):
    print(len(opt))
    for i in range(0,K):
        gurobi_res,res = runlp_z_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal=False)
        if gurobi_res.feasible == True:
            opt = np.array(list(map(lambda y : 1e7 if y == 0 else 1 / y,res)))
            number_of_states = len(list(filter(lambda x: x > 0, res)))
            print("\nsubsystem size:" + str(number_of_states))
            print("\npr_min: " + str(res[initial]))
        else:
            break
    return gurobi_res,res

def compute_minimal_prmax(N,A,initial,P,to_target,thr,enabled_actions):
    opt = np.ones(N*A)
    return runlp_y_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal=True)

def compute_minimal_prmin(N,A,initial,P,to_target,thr,enabled_actions):
    opt = np.ones(N)
    return runlp_z_lb(N,A,initial,P,to_target,opt,thr,enabled_actions,minimal=True)

def compute_minimal_prmax_ltlsubsys(N,A,initial,P,to_target,thr,enabled_actions):
    I = dok_matrix((A*N,N))
    for n in range(0,N):
        for k in range(0,A):
            if k in enabled_actions[n]:
                I[get_row_index(A,n,k),n] = 1

    #print(I)
    rhs = np.zeros(A*N)
    for i in range(0,A*N):
        rhs[i] = to_target[i] + 1
    #rhs = to_target.copy() + np.ones(A*N)
    rhs.resize((A*N)+1)
    rhs[A*N] = -thr
    delta = np.zeros(N)
    delta[initial] = 1

    A_ub = vstack(((I-P),-delta))

    ## binary select variables that encode an MD scheduler
    I2 = dok_matrix((A*N+1,A*N))
    for n in range(0,A*N):
        I2[n,n] = 1
    A_ub2 = hstack((A_ub,I2))

    binary_vars = range(N,N + A*N)

    ## the sum of actions in a state needs t be positive if the state is positive

    I3 = dok_matrix((N,N))
    for n in range(0,N):
        I3[n,n] = 1

    sum_constraints = hstack((I3,-I.T))
    A_ub3 = vstack((A_ub2,sum_constraints))

    rhs.resize(N + (A*N) + 1)

    opt = np.zeros(N+(A*N))
    for i in range(N,N+(A*N)):
        opt[i] = 1


    return run_gurobi(opt,A_ub3,rhs,set_binary=binary_vars)

