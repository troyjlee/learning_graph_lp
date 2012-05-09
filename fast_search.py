#####################
# For larger graphs search_sched.py can take a long time.
# 
# This program uses a more limited search space to speed things up.
# It only cycles over schedules where first all
# vertices are loaded, then all edges.
# 
# All of the graphs I have tested so far have had optimal 
# schedules of this form.
#
# All the user needs to set is the graph variable in the beginning
# of the main block.
#####################

from copy import deepcopy
from pymprog import *
from itertools import *
from lg_algo import find_params, print_params


def invert_dict(d):
    inv = {}
    for key in d:
        val = d[key]
        if val not in inv:
            inv[val] = key
        else:
            inv[val].append(key)
    return inv


def sched(graph, n):
    m = len(graph)
    inv_graph = invert_dict(graph)
    for v in permutations(range(1, n+1)):
        for e in permutations(range(1, m+1)):
            s = [v[i] for i in range(n)]
            edg = [inv_graph[e[i]] for i in range(m)] 
            s = s + edg
            param = find_params(graph, n, s)
            obj = param[0].primal
            if best == []: 
                best.append(obj)
                sbest.append(s)
                print best
                print sbest
            elif obj < best[-1]:
                best.append(obj)
                sbest.append(s)
                print best
                print sbest


###################
# dictionary with the edges and edge numbers
triangle = { (1,2) : 1, (3,2) : 2, (3,1) : 3}
assoc = {(1,2):1, (2,3):2, (3,4):3, (4,5):4}
dist = {(1,2):1, (2,3):2, (1,3):3, (4,3):4, (5,6):5}
four_clique = {(1,2):1, (1,3):2, (1,4):3, (2,3):4, (2,4):5, (3,4):6}
####################

if __name__ == '__main__':
    # set the input graph here
    graph = four_clique

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
    sched(graph, n)
    print 'progression of best objective values and accompanying schedule'
    print best
    print sbest
    print
    print 'Best schedule found is ', sbest[-1]
    print 'Parameters for this schedule are'
    param = find_params(graph, n, sbest[-1])
    print_params(graph, n, param)
