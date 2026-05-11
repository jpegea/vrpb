from structure import solution
from constructives import cgreedy
import random

def construct(inst, alpha, order='first_linehauls'):

    sol = solution.create_empty_solution(inst)
    cl = add_initial_nodes_and_create_cl(sol, alpha, order)  # ['of_var', 'k', 'i', 'node_id']

    while not sol['feasible']:

        # Si no queden nodes possibles per a afegir, tornem a començar
        if not cl:
            print("Solució no factible")
            sol = solution.create_empty_solution(inst)
            cl = add_initial_nodes_and_create_cl(sol, alpha, order)
            continue

        c_min, c_max = eval_c_min_c_max(cl)
        threshold = c_min + alpha * (c_max - c_min)
        rcl = []

        for c in cl:
            if c[0] <= threshold:
                rcl.append(c)

        sel_idx = random.randint(0, len(rcl) - 1)

        sel_id = rcl[sel_idx][3]
        sel_k = rcl[sel_idx][1]
        sel_pos = rcl[sel_idx][2]
        sel_of_var = rcl[sel_idx][0]

        solution.insert_candidate(sol, sel_id, sel_k, sel_pos, sel_of_var)

        if not sol['pending_linehauls'] and not sol['pending_backhauls']:
            sol['feasible'] = True

        elif order == 'both':
            cl = cgreedy.update_candidate_list_linehauls_and_backhauls(sol, cl, sel_id, sel_k)

        elif not sol['pending_linehauls']:
            last_node_type = sol['instance']['nodes'][sel_id][0]
            if last_node_type == 1:
                cl = cgreedy.create_candidate_list_first_linehauls(sol)
            else:
                cl = cgreedy.update_candidate_list_first_linehauls(sol, cl, sel_id, sel_k)

        else:
            cl = cgreedy.update_candidate_list_first_linehauls(sol, cl, sel_id, sel_k)

    return sol


def eval_c_min_c_max(cl):
    c_min, c_max = float('inf'), float('-inf')
    for c in cl:
        c_min = min(c_min, c[0])
        c_max = max(c_max, c[0])
    return c_min, c_max


def add_initial_nodes_and_create_cl(sol, alpha, order):

    if order == 'both':
        cl = cgreedy.create_candidate_list_linehauls_and_backhauls(sol)
    else:
        cl = cgreedy.create_candidate_list_first_linehauls(sol)  # ['of_var', 'k', 'i', 'node_id']

    for k in range(sol['instance']['l']):

        candidates = [c for c in cl if c[1] == k]

        if not candidates:
            continue

        c_min, c_max = eval_c_min_c_max(candidates)
        threshold = c_max - alpha * (c_max - c_min)
        rcl = []

        for c in candidates:
            if c[0] >= threshold:
                rcl.append(c)

        if rcl:
            sel_idx = random.randint(0, len(rcl) - 1)

            sel_id = rcl[sel_idx][3]
            sel_pos = rcl[sel_idx][2]
            sel_of_var = rcl[sel_idx][0]

            solution.insert_candidate(sol, sel_id, k, sel_pos, sel_of_var)

            if order == 'both':
                cl = cgreedy.update_candidate_list_linehauls_and_backhauls(sol, cl, sel_id, k)
            else:
                cl = cgreedy.update_candidate_list_first_linehauls(sol, cl, sel_id, k)

    return cl