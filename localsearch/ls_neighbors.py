from localsearch import ls_full
from structure import solution


def vnd(sol: dict, neighbors: dict, strategy_intra: str='first', strategy_inter: str='first'):
    l = sol['instance']['l']
    for k in range(l):
        ls_full.improve_route(sol, k, strategy_intra)
        
    improvement = True
    while improvement:
        improvement = inter_swap(sol, strategy_inter, strategy_intra)
        if not improvement:
            improvement = inter_shift(sol, strategy_inter, strategy_intra)



def inter_shift(sol: dict, neighbors: dict, strategy: str='first', strategy_intra: str='first'):

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

                i_neighbors = neighbors[i_id]

                # Restricció de capacitat

                if i_type == 1:
                    load_l = delivery_load_l
                else:
                    load_l = pickup_load_l

                if i_demand + load_l > q:
                    continue

                for j in range(len(route_l) - 1):

                    j_id = route_l[j]
                    next_j_id = route_l[j + 1]

                    # Cerca local restringida a veïns

                    if j_id not in i_neighbors and next_j_id not in i_neighbors:
                        continue

                    j_data = nodes[j_id]
                    j_type = j_data[0]

                    # Restricció de precedència

                    if i_type == 1 and j_type == 2:
                        break

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
                            ls_full.improve_route(sol, sel_routes[0], strategy_intra)
                            ls_full.improve_route(sol, sel_routes[1], strategy_intra)
                            return True

    if best_of_var < 0:
        solution.do_inter_shift(sol, sel_routes, sel_nodes, best_of_var)
        ls_full.improve_route(sol, sel_routes[0], strategy_intra)
        ls_full.improve_route(sol, sel_routes[1], strategy_intra)
        return True

    return False


def inter_swap(sol: dict, neighbors: dict, strategy: str='first', strategy_intra: str='first'):

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

                i_neighbors = neighbors[i_id]

                prev_i_id = route_k[i - 1]
                prev_i_data = nodes[prev_i_id]
                prev_i_type = prev_i_data[0]

                next_i_id = route_k[i + 1]
                next_i_data = nodes[next_i_id]
                next_i_type = next_i_data[0]

                for j in range(1, len(route_l) - 1):

                    j_id = route_l[j]

                    # Cerca local restringida a veïns

                    if j_id not in i_neighbors:
                        continue

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
                            ls_full.improve_route(sol, sel_routes[0], strategy_intra)
                            ls_full.improve_route(sol, sel_routes[1], strategy_intra)
                            return True

    # Best improvement
    if best_of_var < 0:
        solution.do_inter_swap(sol, sel_routes, sel_nodes, best_of_var)
        ls_full.improve_route(sol, sel_routes[0], strategy_intra)
        ls_full.improve_route(sol, sel_routes[1], strategy_intra)
        return True

    return False