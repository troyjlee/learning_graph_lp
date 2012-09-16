################
# Given a graph and a loading schedule
# this program formulates a linear program 
# to find the parameters and cost of the 
# learning graph algorithm given in the paper
# "Improved Algorithms for triangle finding and associativity testing"
# by Lee, Magniez, and Santha
#
# In main the user can set the variables graph and schedule
# To solve the linear program we use the package PyMathProg
# which can be downloaded at http://pymprog.sourceforge.net/
#
# Organization of variables in the linear program:
# The first variable is the objective---this is the cost of the algorithm
#
# The next n variables are the set size parameters r_1, ..., r_n
#
# The graph is represented as a dictionary with edges mapped to labels 
# 1, ..., number of edges.  The next (2* number of edges) variables give the 
# degree parameters.  Two variables are used for each degree parameter as 
# the solver glpk assumes all variables are non-negative.  The first variable is the 
# positive term and the second the negative term.  For the edge (i,j) the 
# corresponding degree parameter gives the average degree in set i going to set j.
# Note that this representation is different from that given in the paper as we 
# do not know before hand the sizes of the sets.
################ 

from copy import deepcopy
from pymprog import *

# given a set of loaded vertices and loaded edges, this function 
# computes the vertex ratio
def vertex_ratio(vertices_loaded, edges_loaded, graph, n):
    numvars = 1 + n + 2*len(graph)
    num_vertices = len(vertices_loaded)
    nterm = -num_vertices/2.0
    row = [0 for i in range(numvars)]
    row[0] = -1.
    for v in vertices_loaded:
        row[v] += -.5
    for e in edges_loaded:
        row[n + 2*graph[e]-1] += -.5
        row[n + 2*graph[e]] += .5
        row[e[1]] += .5
    return nterm, row

# this function adds a constraint for the cost of loading the vertex a
# given vertices_loaded and edges_loaded
def load_vertex(A, b, a, vertices_loaded, edges_loaded, graph, n):
    (nterm, preterm) = vertex_ratio(vertices_loaded, edges_loaded, graph, n)
    nterm -= .5
    for v in range(1, n+1):
        av = graph.get((a, v), -1)
        if av > 0:
            row = deepcopy(preterm)
            row[n + 2*av-1] += 1.;
            row[n + 2*av] -= 1.;
            A.append(row)
            b.append(nterm)
        va = graph.get((v, a), -1)
        if va > 0:
            row = deepcopy(preterm)
            row[n + 2*va-1] += 1.;
            row[n + 2*va] -= 1.;
            row[v] += 1.
            row[a] -= 1.
            A.append(row)
            b.append(nterm)
    return A, b

# this function adds a constraint for the cost of loading the edge ab
# given vertices_loaded and edges_loaded
def load_edge(A, b, ab, vertices_loaded, edges_loaded, graph, n):
    (nterm, row) = vertex_ratio(vertices_loaded, edges_loaded, graph, n)
    row2 = deepcopy(row)
    row[ab[0]] += 1
    A.append(row)
    b.append(nterm)
    row2[ab[1]] += 1
    A.append(row2)
    b.append(nterm)
    return A, b

def last_edge(A, b, ab, vertices_loaded, edges_loaded, graph, n):
    (nterm, row) = vertex_ratio(vertices_loaded, edges_loaded, graph, n)
    row[ab[0]] += 0.5
    row[ab[1]] += 0.5
    A.append(row)
    b.append(nterm)
    return A, b

# this function adds constraints for the setup step.
# Note that we do not include the constraint for item 3 in 
# the definition of admissible parameters.  Thus it should be 
# checked that the optimal parameters obtained actually are 
# admissible
def setup(graph, n):
    A = []
    b = []
    numvars = 1 + n + 2*len(graph)
    # r_j \le n
    for j in range(1, n+1):
        row = [0 for i in range(numvars)]
        row[j]=1;
        A.append(row)
        b.append(1.)
    for e in graph:
        # degree constraint f_ij \le r_j
        row = [0. for i in range(numvars)]
        row[e[1]] = -1.
        row[n + 2*graph[e]-1] = 1.
        row[n + 2*graph[e]] = -1.
        A.append(row)
        b.append(0.)
        # setup cost
        row = [0 for i in range(numvars)]
        row[0] = -1.
        row[e[0]] = 1.
        row[n + 2*graph[e]-1] = 1.
        row[n + 2*graph[e]] = -1.
        A.append(row)
        b.append(0.)
    return A, b

def solve_prog(A, b, numvars):
    num_constraints = len(A)
    xid = range(numvars)
    rid = range(num_constraints)
    c = [1.]
    for i in range(1, numvars):
        c.append(0.)

    beginModel('basic')
    #verbose(True)
    x = var(xid, 'X')
    minimize(x[0], 'myobj')
    r=st( sum(A[i][j] * x[j] for j in xid) <= b[i] for i in rid)
    solve()
    #print "Solver status:", status()
    #print 'obj = %g;' % vobj()
    return x

# this function runs through the loading schedule and calls the appropriate 
# functions to add constraints for each stage of loading a vertex or 
# loading an edge
def find_params(graph, n, schedule):
    (A, b) = setup(graph, n)
    vertices_loaded = []
    edges_loaded = []
    for x in schedule[:-1]:
        if type(x) == int:
            (A, b) = load_vertex(A, b, x, vertices_loaded, edges_loaded, graph, n)
            vertices_loaded.append(x)
        elif type(x) == tuple:
            (A, b) = load_edge(A, b, x, vertices_loaded, edges_loaded, graph, n)
            edges_loaded.append(x)
        else:
            print 'error in schedule'
            break
    (A, b) = last_edge(A, b, schedule[-1], vertices_loaded, edges_loaded, graph, n)
    numvars = 1 + n + 2*len(graph)
    param = solve_prog(A, b, numvars)
    return param

# function takes a decimal number and prints its fractional representation 
# if the denominator is less than 100
def to_frac(dec, tol = 0.0001):
    for y in range(1, 100):
        x = y * dec
        if abs(x - round(x)) < tol:
            print '= %d / %d' % (int(round(x)), y)
            return 1
    print '' 
    return -1

# this function prints out nicely the optimal parameters
def print_params(graph, n, param):
    cost = param[0].primal
    print 'The objective value is %.4f' % cost, 
    to_frac(cost)
    print
    print 'Set size parameters are'
    for i in range(1, n+1):
        r = param[i].primal
        print 'set %d = %.4f' % (i, r),
        to_frac(r)
    print 
    print 'Degree parameters are'
    for e in graph:
        deg = param[n + 2*graph[e]-1].primal - param[n + 2*graph[e]].primal 
        print 'degree from %d to %d = %.4f' % (e[0], e[1], deg),
        to_frac(deg)

###################
# the graph to detect is given as a dictionary 
# with the edges and associated edge number
# the edge number is used for ordering the degree parameter variables
# here are some sample graphs
triangle = { (1,2) : 1, (1,3) : 2, (2,3) : 3}
assoc = {(2,1):1, (2,3):2, (3,4):3, (5,4):4}
dist = {(1,2):1, (2,3):2, (1,3):3, (4,3):4, (5,6):5}
fourclique = {(1,2):1, (1,3):2, (1,4):3, (1,5):4, (2,3):5, (2,4):6, (2,5):7, (3,4):8, (3,5):9, (4,5):10}

# the schedule gives the order to load the vertices and edges
# here are some sample schedules
assoc_schedule = [1, 2, 4, 3, (2,1), (2,3), (3,4), 5, (5,4)]
tri_schedule = [1, 2, 3, (1,2), (2,3), (1,3)]
five_schedule = [1, 2, 3, 4, 5, (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]

###################

if __name__ == '__main__':
    # modify the next two lines to set the input graph and 
    # the loading schedule
    graph = assoc
    schedule = assoc_schedule

    # the next few lines determine the number of vertices from the graph
    vertices = []
    for e in graph:
        if e[0] not in vertices: 
            vertices.append(e[0])
    if e[1] not in vertices:
        vertices.append(e[1])
    n = len(vertices)
 
    param = find_params(graph, n, schedule)
    print_params(graph, n, param)
