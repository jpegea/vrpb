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
        cl = add_initial_nodes_with_demand_priority(sol, alpha, beta, first)
    else:
        cl = add_initial_nodes(sol, alpha, beta, first)

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


def add_initial_nodes(sol: dict, alpha: float, beta: float, first: str='linehauls'):

    n_vehicles = sol['instance']['l']

    cl = cgreedy.create_candidate_list(sol, beta, first)

    for k in range(n_vehicles):

        candidates = [el[1] for el in cl if el[1][1] == k]

        if not candidates:
            break

        c_min, c_max = float('inf'), float('-inf')
        for c in candidates:
            c_min = min(c_min, c[0])
            c_max = max(c_max, c[0])

        threshold = c_max - alpha * (c_max - c_min)
        rcl = [c for c in candidates if c[0] >= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        cl = cgreedy.update_candidate_list(sol, beta, cl, sel, first)

    return cl


def add_initial_nodes_with_demand_priority(sol: dict, alpha: float, beta: float, first: str='linehauls'):

    n_vehicles = sol['instance']['l']

    cl = cgreedy.create_candidate_list(sol, 1, first)

    for k in range(n_vehicles):

        candidates = [el[1] for el in cl if el[1][1] == k]

        if not candidates:
            break

        c_min, c_max = float('inf'), float('-inf')
        for c in candidates:
            c_min = min(c_min, c[0])
            c_max = max(c_max, c[0])

        threshold = c_max - alpha * (c_max - c_min)
        rcl = [c for c in candidates if c[0] >= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        cl = cgreedy.create_candidate_list(sol, beta, first)

    return cl