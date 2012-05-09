######################
# This program runs through all possible loading schedules 
# to find the minimal cost algorithm.
# 
# This program has the code to generate all schedules
# and uses the functions in lg_algo.py to construct and solve 
# the corresponding linear program
#
# in main, the user can modify the graph variable to set the input graph
# For example for triangle one could say
# graph = { (1,2) : 1, (3,2) : 2, (3,1) : 3}
# 
# Further examples are given below
######################


from copy import deepcopy
from lg_algo import find_params, print_params

# This is a recursive function to generate all schedules
# For each schedule generated find_params is called to 
# compute the cost and parameters
# the current best cost and schedules are stored in 
# lists best and sbest, respectively
def sched(s, to_load, graph, n):
    if to_load == []:
        param = find_params(graph, n, s)
        obj = param[0].primal
        if best == []:
            best.append(obj)
            sbest.append(s)
        elif obj < best[-1]:
            best.append(obj)
            sbest.append(s)
    else:
        for v in to_load:
            if (type(v) == tuple and v[0] in s and v[1] in s) or type(v) == int:
                t = deepcopy(s)
                t.append(v)
                branch = [x for x in to_load if x != v]
                sched(t, branch, graph, n)

###################

# dictionary with the edges and edge numbers
triangle = { (1,2) : 1, (3,2) : 2, (3,1) : 3}
assoc = {(1,2):1, (2,3):2, (3,4):3, (4,5):4}
dist = {(1,2):1, (2,3):2, (1,3):3, (4,3):4, (5,6):5}

####################

if __name__ == '__main__':
    # set the input graph here
    graph = triangle

    # the next few lines compute the number of vertices
    vertices = []
    for e in graph:
        if e[0] not in vertices: 
            vertices.append(e[0])
        if e[1] not in vertices:
            vertices.append(e[1])
    n = len(vertices)

    to_load = vertices + graph.keys()
    # best is a list to hold the progression of best costs found
    best = []
    # sbest is a list to hold the progression of corresponding best schedules 
    sbest = []
    s = []
    sched(s, to_load, graph, n)
    print 'progression of best objective values and accompanying schedule'
    print best
    print sbest
    print 
    print 'Best schedule found is ', sbest[-1]
    print 'Parameters for this schedule are'
    param = find_params(graph, n, sbest[-1])
    print_params(graph, n, param)
