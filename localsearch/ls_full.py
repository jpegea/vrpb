from structure import solution

def improve_routes(sol: dict, strategy: str='best', show_operations: bool=False):
    for k in range(sol['instance']['l']):
        improve_intra_route(sol, k, strategy, show_operations)


def improve_inter_route(sol: dict, strategy: str= 'best', show_operations: bool=False):
    improvement = True
    while improvement:
        improvement = inter_shift(sol, strategy)
        if improvement and show_operations:
            print('Inter: Shift')
        if not improvement:
            improvement = inter_swap(sol, strategy)
            if improvement and show_operations:
                print('Inter: Swap')


def improve_intra_route(sol: dict, k: int, strategy: str='best', show_operations: bool=False):
    improvement = True
    while improvement:
        improvement = intra_shift(sol, k, strategy)
        if improvement:
            if show_operations:
                print("Intra: Shift")
        if not improvement:
            improvement = intra_swap(sol, k, strategy)
            if improvement:
                if show_operations:
                    print("Intra: Swap")
        if not improvement:
            improvement = intra_2opt(sol, k, strategy)
            if improvement:
                if show_operations:
                    print("Intra: 2-opt")


def intra_shift(sol: dict, k: int, strategy: str='best'):

    inst = sol['instance']
    route = sol['routes'][k]

    nodes = inst['nodes']
    cost = inst['cost']

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route) - 1):

        i_id = route[i]
        i_data = nodes[i_id]
        i_type = i_data[0]

        prev_i_id = route[i - 1]
        next_i_id = route[i + 1]

        for j in range(len(route) - 1):

            if i - 2 <= j <= i + 1:
                continue

            j_id = route[j]
            j_data = nodes[j_id]
            j_type = j_data[0]

            # Restriccions de precedència

            if i_type == 1 and j_type == 2:
                break

            next_j_id = route[j + 1]
            next_j_data = nodes[next_j_id]
            next_j_type = next_j_data[0]

            if i_type == 2 and next_j_type == 1:
                continue

            # Avaluació

            of_var = cost[prev_i_id][next_i_id] + cost[j_id][i_id] + cost[i_id][next_j_id] - \
                cost[prev_i_id][i_id] - cost[i_id][next_i_id] - cost[j_id][next_j_id]

            of_var = round(of_var, 2)

            if of_var < best_of_var:

                best_of_var = of_var
                selected = (i,j)

                # First improvement
                if strategy == 'first':
                    solution.do_intra_shift(sol, k, selected, best_of_var)
                    return True

    # Best improvement
    if best_of_var < 0:
        solution.do_intra_shift(sol, k, selected, best_of_var)
        return True

    return False


def intra_swap(sol: dict, k: int, strategy: str='best'):

    inst = sol['instance']
    route = sol['routes'][k]

    nodes = inst['nodes']
    cost = inst['cost']

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route) - 2):

        i_id = route[i]
        i_data = nodes[i_id]
        i_type = i_data[0]

        prev_i_id = route[i - 1]
        next_i_id = route[i + 1]

        for j in range(i + 1, len(route) - 1):

            j_id = route[j]
            j_data = nodes[j_id]
            j_type = j_data[0]

            # Restricció de precedència

            if i_type != j_type:
                break

            # Avaluació

            next_j_id = route[j + 1]

            if j_id == next_i_id:
                of_var = cost[prev_i_id][j_id] + cost[i_id][next_j_id] - cost[prev_i_id][i_id] - cost[j_id][next_j_id]
            else:
                prev_j_id = route[j - 1]
                of_var = cost[prev_i_id][j_id] + cost[j_id][next_i_id] + cost[prev_j_id][i_id] + cost[i_id][next_j_id] - \
                    cost[prev_i_id][i_id] - cost[i_id][next_i_id] - cost[prev_j_id][j_id] - cost[j_id][next_j_id]

            of_var = round(of_var, 2)

            if of_var < best_of_var:

                best_of_var = of_var
                selected = (i,j)

                # First improvement
                if strategy == 'first':
                    solution.do_intra_swap(sol, k, selected, best_of_var)
                    return True

    # Best improvement
    if best_of_var < 0:
        solution.do_intra_swap(sol, k, selected, best_of_var)
        return True

    return False


def intra_2opt(sol: dict, k: int, strategy: str='best'):

    inst = sol['instance']
    route = sol['routes'][k]

    nodes = inst['nodes']
    cost = inst['cost']

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route) - 2):

        i_id = route[i]
        i_data = nodes[i_id]
        i_type = i_data[0]

        prev_i_id = route[i - 1]

        for j in range(i + 2, len(route) - 1):

            j_id = route[j]
            j_data = nodes[j_id]
            j_type = j_data[0]

            # Restricció de precedència

            if i_type != j_type:
                break

            next_j_id = route[j + 1]

            # Avaluació

            of_var = cost[prev_i_id][j_id] + cost[i_id][next_j_id] - cost[prev_i_id][i_id] - cost[j_id][next_j_id]

            of_var = round(of_var, 2)

            if of_var < best_of_var:

                best_of_var = of_var
                selected = (i,j)

                # First improvement
                if strategy == 'first':
                    solution.do_intra_2opt(sol, k, selected, best_of_var)
                    return True

    # Best improvement
    if best_of_var < 0:
        solution.do_intra_2opt(sol, k, selected, best_of_var)
        return True

    return False


def inter_shift(sol: dict, strategy: str='best'):

    inst = sol['instance']
    nodes = inst['nodes']
    cost = inst['cost']
    q = inst['q']
    n_vehicles = inst['l']

    routes = sol['routes']
    delivery_load = sol['delivery']
    pickup_load = sol['pickup']

    best_of_var = 0
    sel_routes = (0, 0)
    sel_nodes = (0, 0)

    for k in range(n_vehicles):

        route_k = routes[k]

        for l in range(n_vehicles):

            if k == l:
                continue

            route_l = routes[l]

            delivery_load_l = delivery_load[l]
            pickup_load_l = pickup_load[l]

            for i in range(1, len(route_k) - 1):

                i_id = route_k[i]
                i_data = nodes[i_id]
                i_type = i_data[0]
                i_demand = i_data[3]

                # Restricció de capacitat

                if i_type == 1:
                    load_l = delivery_load_l
                else:
                    load_l = pickup_load_l

                if i_demand + load_l > q:
                    continue

                for j in range(len(route_l) - 1):

                    j_id = route_l[j]
                    j_data = nodes[j_id]
                    j_type = j_data[0]

                    # Restricció de precedència

                    if i_type == 1 and j_type == 2:
                        break

                    next_j_id = route_l[j + 1]
                    next_j_data = nodes[next_j_id]
                    next_j_type = next_j_data[0]

                    if i_type == 2 and next_j_type == 1:
                        continue

                    # Avaluació

                    prev_i_id = route_k[i - 1]
                    next_i_id = route_k[i + 1]

                    of_var = cost[prev_i_id][next_i_id] + cost[j_id][i_id] + cost[i_id][next_j_id] - \
                        cost[prev_i_id][i_id] - cost[i_id][next_i_id] - cost[j_id][next_j_id]

                    of_var = round(of_var, 2)

                    if of_var < best_of_var:

                        best_of_var = of_var
                        sel_routes = (k, l)
                        sel_nodes = (i, j)

                        # First improvement
                        if strategy == 'first':
                            solution.do_inter_shift(sol, sel_routes, sel_nodes, best_of_var)
                            improve_intra_route(sol, sel_routes[0], strategy)
                            improve_intra_route(sol, sel_routes[1], strategy)
                            return True

    if best_of_var < 0:
        solution.do_inter_shift(sol, sel_routes, sel_nodes, best_of_var)
        improve_intra_route(sol, sel_routes[0], strategy)
        improve_intra_route(sol, sel_routes[1], strategy)
        return True

    return False


def inter_swap(sol: dict, strategy: str='best'):

    inst = sol['instance']
    nodes = inst['nodes']
    cost = inst['cost']
    q = inst['q']
    n_vehicles = inst['l']

    routes = sol['routes']
    delivery_load = sol['delivery']
    pickup_load = sol['pickup']

    best_of_var = 0
    sel_routes = (0, 0)
    sel_nodes = (0, 0)

    for k in range(n_vehicles):

        route_k = routes[k]

        delivery_load_k = delivery_load[k]
        pickup_load_k = pickup_load[k]

        for l in range(k + 1, n_vehicles):

            route_l = routes[l]

            delivery_load_l = delivery_load[l]
            pickup_load_l = pickup_load[l]

            for i in range(1, len(route_k) - 1):

                i_id = route_k[i]
                i_data = nodes[i_id]
                i_type = i_data[0]
                i_demand = i_data[3]

                prev_i_id = route_k[i - 1]
                prev_i_data = nodes[prev_i_id]
                prev_i_type = prev_i_data[0]

                next_i_id = route_k[i + 1]
                next_i_data = nodes[next_i_id]
                next_i_type = next_i_data[0]

                for j in range(1, len(route_l) - 1):

                    j_id = route_l[j]
                    j_data = nodes[j_id]
                    j_type = j_data[0]

                    # Restriccions de precedència

                    prev_j_id = route_l[j - 1]
                    prev_j_data = nodes[prev_j_id]
                    prev_j_type = prev_j_data[0]

                    if i_type == 1 and prev_j_type == 2:
                        break

                    if j_type == 1 and prev_i_type == 2:
                        continue

                    next_j_id = route_l[j + 1]
                    next_j_data = nodes[next_j_id]
                    next_j_type = next_j_data[0]

                    if i_type == 2 and next_j_type == 1:
                        continue

                    if j_type == 2 and next_i_type == 1:
                        break

                    # Restricció de capacitat

                    j_demand = j_data[3]

                    if j_type == 1:
                        load_k = delivery_load_k
                    else:
                        load_k = pickup_load_k

                    if i_type == 1:
                        load_l = delivery_load_l
                    else:
                        load_l = pickup_load_l

                    if i_type == j_type:
                        load_k -= i_demand
                        load_l -= j_demand

                    if i_demand + load_l > q:
                        continue

                    if j_demand + load_k > q:
                        continue

                    # Avaluació

                    of_var = cost[prev_i_id][j_id] + cost[j_id][next_i_id] + cost[prev_j_id][i_id] + cost[i_id][next_j_id] - \
                        cost[prev_i_id][i_id] - cost[i_id][next_i_id] - cost[prev_j_id][j_id] - cost[j_id][next_j_id]

                    of_var = round(of_var, 2)

                    if of_var < best_of_var:

                        best_of_var = of_var
                        sel_routes = (k, l)
                        sel_nodes = (i, j)

                        # First improvement
                        if strategy == 'first':
                            solution.do_inter_swap(sol, sel_routes, sel_nodes, best_of_var)
                            improve_intra_route(sol, sel_routes[0], strategy)
                            improve_intra_route(sol, sel_routes[1], strategy)
                            return True

    # Best improvement
    if best_of_var < 0:
        solution.do_inter_swap(sol, sel_routes, sel_nodes, best_of_var)
        improve_intra_route(sol, sel_routes[0], strategy)
        improve_intra_route(sol, sel_routes[1], strategy)
        return True

    return False