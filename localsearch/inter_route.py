from structure import solution

def shift(sol, strategy='best'):

    best_of_var = 0
    selected_routes = (0,0)
    selected_nodes = (0,0)

    for k in range(sol['instance']['l']):
        for l in range(sol['instance']['l']):

            if k == l:
                continue

            route_k = sol['routes'][k]
            route_l = sol['routes'][l]

            for i in range(1, len(route_k) - 1):

                node_i = sol['instance']['nodes'][route_k[i]]

                # Restricció de capacitat
                load_l = sol['delivery' if node_i[0] == 1 else 'pickup'][l]
                if node_i[3] + load_l > sol['instance']['q']:
                    continue

                for j in range(len(route_l) - 1):

                    node_j = sol['instance']['nodes'][route_l[j]]

                    # Evita fer entrega després de recollida
                    if node_i[0] == 1 and node_j[0] == 2:
                        break

                    # Evita fer recollida abans d'entrega
                    next_node_j = sol['instance']['nodes'][route_l[j + 1]]
                    if node_i[0] == 2 and next_node_j[0] == 1:
                        continue

                    of_var = round(
                        sol['instance']['cost'][route_k[i - 1]][route_k[i + 1]] + \
                        sol['instance']['cost'][route_l[j]][route_k[i]] + \
                        sol['instance']['cost'][route_k[i]][route_l[j + 1]] - \
                        sol['instance']['cost'][route_k[i - 1]][route_k[i]] - \
                        sol['instance']['cost'][route_k[i]][route_k[i + 1]] - \
                        sol['instance']['cost'][route_l[j]][route_l[j + 1]], 2)

                    if of_var < best_of_var:
                        best_of_var = of_var
                        selected_routes = (k, l)
                        selected_nodes = (i, j)
                        if strategy == 'first':
                            solution.do_inter_shift(sol, selected_routes, selected_nodes, best_of_var)
                            return True

    if best_of_var < 0:
        solution.do_inter_shift(sol, selected_routes, selected_nodes, best_of_var)
        return True

    return False


def swap(sol, strategy='best'):

    best_of_var = 0
    selected_routes = (0,0)
    selected_nodes = (0,0)

    for k in range(sol['instance']['l']):
        for l in range(k + 1, sol['instance']['l']):

            route_k = sol['routes'][k]
            route_l = sol['routes'][l]

            for i in range(1, len(route_k) - 1):

                for j in range(1, len(route_l) - 1):

                    node_i = sol['instance']['nodes'][route_k[i]]
                    node_j = sol['instance']['nodes'][route_l[j]]

                    # Restricció de capacitat
                    load_k = sol['delivery' if node_j[0] == 1 else 'pickup'][k]
                    load_l = sol['delivery' if node_i[0] == 1 else 'pickup'][l]

                    if node_i[0] == node_j[0]:
                        load_k -= node_i[3]
                        load_l -= node_j[3]

                    if node_i[3] + load_l > sol['instance']['q']:
                        continue

                    if node_j[3] + load_k > sol['instance']['q']:
                        continue

                    # Evita fer entrega després de recollida
                    prev_node_j = sol['instance']['nodes'][route_l[j - 1]]
                    if node_i[0] == 1 and prev_node_j[0] == 2:
                        break

                    prev_node_i = sol['instance']['nodes'][route_k[i - 1]]
                    if node_j[0] == 1 and prev_node_i[0] == 2:
                        continue

                    # Evita fer recollida abans d'entrega
                    next_node_j = sol['instance']['nodes'][route_l[j + 1]]
                    if node_i[0] == 2 and next_node_j[0] == 1:
                        continue

                    next_node_i = sol['instance']['nodes'][route_k[i + 1]]
                    if node_j[0] == 2 and next_node_i[0] == 1:
                        break

                    of_var = round(
                        sol['instance']['cost'][route_k[i - 1]][route_l[j]] + \
                        sol['instance']['cost'][route_l[j]][route_k[i + 1]] + \
                        sol['instance']['cost'][route_l[j - 1]][route_k[i]] + \
                        sol['instance']['cost'][route_k[i]][route_l[j + 1]] - \
                        sol['instance']['cost'][route_k[i - 1]][route_k[i]] - \
                        sol['instance']['cost'][route_k[i]][route_k[i + 1]] -
                        sol['instance']['cost'][route_l[j - 1]][route_l[j]] -
                        sol['instance']['cost'][route_l[j]][route_l[j + 1]], 2)

                    if of_var < best_of_var:
                        best_of_var = of_var
                        selected_routes = (k, l)
                        selected_nodes = (i, j)
                        if strategy == 'first':
                            solution.do_inter_swap(sol, selected_routes, selected_nodes, best_of_var)
                            return True

    if best_of_var < 0:
        solution.do_inter_swap(sol, selected_routes, selected_nodes, best_of_var)
        return True

    return False