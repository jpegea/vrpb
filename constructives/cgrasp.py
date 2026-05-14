from structure import solution
from constructives import cgreedy
import random

def construct(inst, alpha, first='both'):

    sol = solution.create_empty_solution(inst)

    cl = add_initial_nodes(sol, alpha, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            print("Solució no factible")
            sol = solution.create_empty_solution(inst)
            cl = add_initial_nodes(sol, alpha, first)
            continue

        c_min, c_max = float('inf'), float('-inf')
        for c in cl:
            c_min = min(c_min, c[0])
            c_max = max(c_max, c[0])

        threshold = c_min + alpha * (c_max - c_min)
        rcl = [c for c in cl if c[0] <= threshold]

        sel_idx = random.randint(0, len(rcl) - 1)

        sel = rcl[sel_idx]
        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = cgreedy.create_candidate_list(sol, 'linehauls')
        else:
            cl = cgreedy.update_candidate_list(sol, cl, sel, first)

    return sol


def add_initial_nodes(sol, alpha, first='both'):

    n_vehicles = sol['instance']['l']

    cl = cgreedy.create_candidate_list(sol, first)

    for k in range(n_vehicles):

        candidates = [c for c in cl if c[1] == k]

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

        cl = cgreedy.update_candidate_list(sol, cl, sel, first)

    return cl