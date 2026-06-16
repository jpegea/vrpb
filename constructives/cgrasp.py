from structure import solution
from constructives import cgreedy
import random

def construct(inst: dict, alpha: float, beta: float, first: str='linehauls'):

    sol = solution.create_empty_solution(inst)
    cl = cgreedy.create_candidate_list(sol, beta, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            return sol

        min_score, max_score = float('inf'), float('-inf')
        for c in cl:
            min_score = min(min_score, c[0])
            max_score = max(max_score, c[0])

        threshold = min_score + alpha * (max_score - min_score)
        rcl = [c[1] for c in cl if c[0] <= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel: tuple[float, int, int, int] = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = cgreedy.create_candidate_list(sol, beta, first)
        else:
            cl = cgreedy.update_candidate_list(sol, beta, cl, sel, first)

    return sol


def construct_with_initial_nodes(inst:dict, alpha: float, beta: float, first: str='linehauls', priority: str='distance'):

    sol = solution.create_empty_solution(inst)
    if priority == 'demand':
        add_initial_nodes_with_demand_priority(sol, alpha)
    elif priority == 'distance':
        add_initial_nodes_with_distance_priority(sol, alpha)
    else:
        print('ERROR GARRAFAL')
        return sol
    
    cl = cgreedy.create_candidate_list(sol, beta, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            return sol

        min_score, max_score = float('inf'), float('-inf')
        for c in cl:
            min_score = min(min_score, c[0])
            max_score = max(max_score, c[0])

        threshold = min_score + alpha * (max_score - min_score)
        rcl = [c[1] for c in cl if c[0] <= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = cgreedy.create_candidate_list(sol, beta, first)
        else:
            cl = cgreedy.update_candidate_list(sol, beta, cl, sel, first)

    return sol


def add_initial_nodes_with_distance_priority(sol: dict, alpha: float):
    inst = sol['instance']
    cost = inst['cost']
    n_vehicles = inst['l']

    pending_linehauls = sol['pending_linehauls']
    routes = sol['routes']

    for k in range(n_vehicles):

        if not pending_linehauls:
            break

        cl: list[tuple[float, int]] = []
        max_dist, min_dist = float('-inf'), float('inf')
        for n_id in pending_linehauls:
            dist = cost[0][n_id] + sum(cost[n_id][routes[l][1]] for l in range(k-1))
            cl.append((dist, n_id))
            max_dist = max(max_dist, dist)
            min_dist = min(min_dist, dist)
            
        threshold = max_dist - alpha * (max_dist - min_dist)
        rcl = [c for c in cl if c[0] >= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)
        node_id = rcl[sel_idx][1]

        of_var = 2 * cost[0][node_id]
        solution.insert_candidate(sol, (of_var, k, 1, node_id))


def add_initial_nodes_with_demand_priority(sol: dict, alpha: float):

    n_vehicles = sol['instance']['l']

    cl = cgreedy.create_candidate_list(sol, 1, 'linehauls')

    for k in range(n_vehicles):

        candidates = [c for c in cl if c[1][1] == k]

        if not candidates:
            break

        c_min, c_max = float('inf'), float('-inf')
        for c in candidates:
            c_min = min(c_min, c[0])
            c_max = max(c_max, c[0])

        threshold = c_min + alpha * (c_max - c_min)
        rcl = [c[1] for c in candidates if c[0] <= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        cl = cgreedy.update_candidate_list(sol, 1, cl, sel, 'linehauls')