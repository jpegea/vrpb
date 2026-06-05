from structure import solution

def construct(inst: dict, beta: float, first: str='linehauls'):

    sol = solution.create_empty_solution(inst)
    cl = create_candidate_list(sol, beta, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            print("No s'ha trobat una solució factible")
            return sol

        min_score, sel = float('inf'), (0, 0, 0, 0)

        for c in cl:
            if c[0] < min_score:
                min_score = c[0]
                sel = c[1]

        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = create_candidate_list(sol, beta,  'linehauls')
        else:
            cl = update_candidate_list(sol, beta, cl, sel, first)

    return sol


def construct_with_initial_nodes(inst: dict, beta: float, first: str='linehauls', priority='distance'):

    sol = solution.create_empty_solution(inst)

    if priority == 'demand':
        cl = add_initial_nodes_with_demand_priority(sol, beta, first)
    else:
        cl = add_initial_nodes(sol, beta, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            print("No s'ha trobat una solució factible")
            return sol

        min_score, sel = float('inf'), (0, 0, 0, 0)

        for c in cl:
            if c[0] < min_score:
                min_score = c[0]
                sel = c[1]

        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = create_candidate_list(sol, beta,  'linehauls')
        else:
            cl = update_candidate_list(sol, beta, cl, sel, first)

    return sol


def add_initial_nodes(sol: dict, beta: float, first: str='linehauls'):

    n_vehicles = sol['instance']['l']

    cl = create_candidate_list(sol, beta, first)

    for k in range(n_vehicles):

        if not cl:
            break

        score_max, sel = 0, (0.0, 0, 0, 0)

        for c in cl:
            if c[1][1] != k:
                continue
            if c[0] > score_max:
                score_max = c[0]
                sel = c[1]

        solution.insert_candidate(sol, sel)
        cl = update_candidate_list(sol, beta, cl, sel, first)

    return cl


def add_initial_nodes_with_demand_priority(sol: dict, beta: float, first: str='linehauls'):

    inst = sol['instance']
    nodes = inst['nodes']
    cost = inst['cost']
    n_vehicles = inst['l']

    pending_linehauls = sol['pending_linehauls']

    sorted_nodes = sorted(
        pending_linehauls,
        key=lambda n_id: nodes[n_id][3],
        reverse=True
    )

    for k in range(n_vehicles):
        node_id = sorted_nodes[k]
        of_var = 2 * cost[0][node_id]
        solution.insert_candidate(sol, (of_var, k, 1, node_id))

    cl = create_candidate_list(sol, beta, first)

    return cl


def create_candidate_list(sol: dict, beta: float, first: str='linehauls'):

    inst = sol['instance']
    nodes = inst['nodes']
    cost = inst['cost']
    routes = sol['routes']

    n_vehicles = inst['l']
    q = inst['q']

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']

    if first == 'linehauls':
        pending = pending_linehauls if pending_linehauls else pending_backhauls
    else:
        pending = pending_linehauls.union(pending_backhauls)

    cl = []

    for node_id in pending:

        node_data = nodes[node_id]
        node_type = node_data[0]
        node_demand = node_data[3]

        load = sol['delivery' if node_type == 1 else 'pickup']

        for k in range(n_vehicles):

            # Restricció de capacitat

            if node_demand + load[k] > q:
                continue

            route = routes[k]

            for j in range(1, len(route)):

                # Restriccions de precedència

                prev_id = route[j - 1]
                prev_data = nodes[prev_id]
                prev_type = prev_data[0]

                if node_type == 1 and prev_type == 2:
                    break

                next_id = route[j]
                next_data = nodes[next_id]
                next_type = next_data[0]

                if node_type == 2 and next_type == 1:
                    continue

                # Avaluació

                of_var = cost[prev_id][node_id] + cost[node_id][next_id] - cost[prev_id][next_id]
                of_var = round(of_var, 2)

                score = (1 - beta) * of_var - beta * node_demand

                cl.append((score, (of_var, k, j, node_id)))

    return cl


def update_candidate_list(sol: dict, beta: float, cl: list, added: tuple, first: str='linehauls'):

    _, modified_k, _, added_id = added

    inst = sol['instance']
    nodes = inst['nodes']
    cost = inst['cost']
    q = inst['q']

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']

    if first == 'linehauls':
        pending = pending_linehauls if pending_linehauls else pending_backhauls
    else:
        pending = pending_linehauls.union(pending_backhauls)

    # Es mantenen els candidats que no siguen el node que ja hem afegit ni la ruta que hem modificat
    new_cl = [el for el in cl if el[1][3] != added_id and el[1][1] != modified_k]

    route = sol['routes'][modified_k]

    load_delivery = sol['delivery'][modified_k]
    load_pickup = sol['pickup'][modified_k]

    for node_id in pending:

        node_data = nodes[node_id]
        node_type = node_data[0]
        node_demand = node_data[3]

        # Restricció de capacitat

        load = load_delivery if node_type == 1 else load_pickup

        if node_demand + load > q:
            continue

        for j in range(1, len(route)):

            # Restriccions de precedència

            prev_id = route[j - 1]
            prev_data = nodes[prev_id]
            prev_type = prev_data[0]

            if node_type == 1 and prev_type == 2:
                break

            next_id = route[j]
            next_data = nodes[next_id]
            next_type = next_data[0]

            if node_type == 2 and next_type == 1:
                continue

            # Avaluació

            of_var = cost[prev_id][node_id] + cost[node_id][next_id] - cost[prev_id][next_id]
            of_var = round(of_var, 2)

            score = (1 - beta) * of_var - beta * node_demand

            new_cl.append((score, (of_var, modified_k, j, node_id)))

    return new_cl