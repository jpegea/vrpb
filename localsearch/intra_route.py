from structure import solution

def shift(sol, k, strategy='best'):

    route = sol['routes'][k]

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route)-1):
        node_i = sol['instance']['nodes'][route[i]]

        for j in range(len(route)-1):

            if i == j or j == i - 1:
                continue

            node_j = sol['instance']['nodes'][route[j]]

            # Evita fer entrega després de recollida
            if node_i[0] == 1 and node_j[0] == 2:
                break

            next_node_j = sol['instance']['nodes'][route[j + 1]]

            # Evita fer recollida abans d'entrega
            if node_i[0] == 2 and next_node_j[0] == 1:
                continue

            of_var = round(
                sol['instance']['cost'][route[i - 1]][route[i + 1]] + \
                sol['instance']['cost'][route[j]][route[i]] + \
                sol['instance']['cost'][route[i]][route[j + 1]] - \
                sol['instance']['cost'][route[i - 1]][route[i]] - \
                sol['instance']['cost'][route[i]][route[i + 1]] - \
                sol['instance']['cost'][route[j]][route[j + 1]], 2)

            if of_var < best_of_var:
                best_of_var = of_var
                selected = (i,j)
                if strategy == 'first':
                    solution.do_intra_shift(sol, k, selected, best_of_var)
                    return True

    if best_of_var < 0:
        solution.do_intra_shift(sol, k, selected, best_of_var)
        return True

    return False


def swap(sol, k, strategy='best'):

    route = sol['routes'][k]

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route)-2):
        node_i = sol['instance']['nodes'][route[i]]

        for j in range(i+1, len(route)-1):
            node_j = sol['instance']['nodes'][route[j]]

            # Restricció d'ordre
            if node_i[0] != node_j[0]:
                break

            if j == i + 1:
                # Cas en què els nodes són adjacents (el swap és una insertion)
                of_var = round(
                    sol['instance']['cost'][route[i-1]][route[j]] + \
                    sol['instance']['cost'][route[j]][route[i]] + \
                    sol['instance']['cost'][route[i]][route[j+1]] - \
                    sol['instance']['cost'][route[i-1]][route[i]] - \
                    sol['instance']['cost'][route[i]][route[j]] - \
                    sol['instance']['cost'][route[j]][route[j+1]],
                    2
                )
            else:
                # Cas amb nodes separats
                of_var = round(
                    sol['instance']['cost'][route[i-1]][route[j]] + \
                    sol['instance']['cost'][route[j]][route[i+1]] + \
                    sol['instance']['cost'][route[j-1]][route[i]] + \
                    sol['instance']['cost'][route[i]][route[j+1]] - \
                    sol['instance']['cost'][route[i-1]][route[i]] - \
                    sol['instance']['cost'][route[i]][route[i+1]] - \
                    sol['instance']['cost'][route[j-1]][route[j]] - \
                    sol['instance']['cost'][route[j]][route[j+1]],
                    2
                )

            if of_var < best_of_var:
                best_of_var = of_var
                selected = (i,j)
                if strategy == 'first':
                    solution.do_intra_swap(sol, k, selected, best_of_var)
                    return True

    if best_of_var < 0:
        solution.do_intra_swap(sol, k, selected, best_of_var)
        return True

    return False


def two_opt(sol, k, strategy='best'):

    route = sol['routes'][k]

    best_of_var = 0
    selected = (0,0)

    for i in range(1, len(route)-2):
        node_i = sol['instance']['nodes'][route[i]]

        for j in range(i+2, len(route)-1):
            node_j = sol['instance']['nodes'][route[j]]

            # Restricció d'ordre
            if node_i[0] != node_j[0]:
                break

            of_var = round(
                sol['instance']['cost'][route[i]][route[j+1]] + \
                sol['instance']['cost'][route[i-1]][route[j]] - \
                sol['instance']['cost'][route[i-1]][route[i]] -
                sol['instance']['cost'][route[j]][route[j+1]],
                2
            )

            if of_var < best_of_var:
                best_of_var = of_var
                selected = (i,j)
                if strategy == 'first':
                    solution.do_intra_2opt(sol, k, selected, best_of_var)
                    return True

    if best_of_var < 0:
        solution.do_intra_2opt(sol, k, selected, best_of_var)
        return True

    return False