from structure import solution

def construct(inst, first='both'):

    sol = solution.create_empty_solution(inst)

    cl = add_initial_nodes(sol, first)

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']
    last_linehauls_added = False

    while not sol['feasible']:

        if not cl:
            print("No s'ha trobat una solució factible")
            return sol

        c_min, sel = float('inf'), (0, 0, 0, 0)

        for c in cl:
            if c[0] < c_min:
                c_min = c[0]
                sel = c

        solution.insert_candidate(sol, sel)

        if not pending_linehauls and not pending_backhauls:
            sol['feasible'] = True
        elif first == 'linehauls' and not pending_linehauls and not last_linehauls_added:
            last_linehauls_added = True
            cl = create_candidate_list(sol, 'linehauls')
        else:
            cl = update_candidate_list(sol, cl, sel, first)

    return sol


def add_initial_nodes(sol, first = 'both'):

    n_vehicles = sol['instance']['l']

    cl = create_candidate_list(sol, first)

    for k in range(n_vehicles):

        if not cl:
            break

        max_dist, sel = 0, tuple()

        for c in cl:
            if c[1] != k:
                continue
            if c[0] > max_dist:
                max_dist = c[0]
                sel = c

        solution.insert_candidate(sol, sel)
        cl = update_candidate_list(sol, cl, sel, first)

    return cl


def create_candidate_list(sol, first='both'):

    nodes = sol['instance']['nodes']
    cost = sol['instance']['cost']
    routes = sol['routes']

    n_vehicles = sol['instance']['l']
    q = sol['instance']['q']

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

                cl.append((of_var, k, j, node_id))

    return cl


def update_candidate_list(sol, cl, added, first='both'):

    _, modified_k, _, added_id = added

    nodes = sol['instance']['nodes']
    cost = sol['instance']['cost']

    q = sol['instance']['q']

    pending_linehauls = sol['pending_linehauls']
    pending_backhauls = sol['pending_backhauls']

    if first == 'linehauls':
        pending = pending_linehauls if pending_linehauls else pending_backhauls
    else:
        pending = pending_linehauls.union(pending_backhauls)

    # Es mantenen els candidats que no siguen el node que ja hem afegit ni la ruta que hem modificat
    new_cl = [c for c in cl if c[3] != added_id and c[1] != modified_k]

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

            new_cl.append((of_var, modified_k, j, node_id))

    return new_cl