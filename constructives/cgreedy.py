from structure import solution

def construct(inst, order='first_linehauls'):

    sol = solution.create_empty_solution(inst)
    cl = add_initial_nodes_and_create_cl(sol, order)  # ['of_var', 'k', 'i', 'node_id']
    # cl = create_candidate_list_first_linehauls(sol)

    while not sol['feasible']:

        if not cl:
            print("No s'ha trobat una solució factible")
            return sol

        # Seleccionem de la cl l'element que menys castigue la of.

        c_min, selected = float('inf'), [0, 0, 0, 0]

        for c in cl:
            if c[0] < c_min:
                c_min = c[0]
                selected = c

        sel_id = selected[3]
        sel_pos = selected[2]
        sel_k = selected[1]
        sel_of_var = selected[0]

        solution.insert_candidate(sol, sel_id, sel_k, sel_pos, sel_of_var)

        # Com que estem gastant fent linehauls i després backhauls, hem de generar la llista completa quan s'acaben els
        # nodes de linehaul.
        if not sol['pending_linehauls'] and not sol['pending_backhauls']:
            sol['feasible'] = True

        elif order == 'both':
            cl = update_candidate_list_linehauls_and_backhauls(sol, cl, sel_id, sel_k)

        elif not sol['pending_linehauls']:
            last_node_type = sol['instance']['nodes'][sel_id][0]
            if last_node_type == 1:
                cl = create_candidate_list_first_linehauls(sol)
            else:
                cl = update_candidate_list_first_linehauls(sol, cl, sel_id, sel_k)

        else:
            cl = update_candidate_list_first_linehauls(sol, cl, sel_id, sel_k)

    return sol


def add_initial_nodes_and_create_cl(sol, order):

    if order == 'both':
        cl = create_candidate_list_linehauls_and_backhauls(sol)
    else:
        cl = create_candidate_list_first_linehauls(sol)  # ['of_var', 'k', 'i', 'node_id']

    for k in range(sol['instance']['l']):

        max_dist, selected = 0, None

        for c in cl:

            if c[1] != k:
                continue

            if c[0] > max_dist:
                max_dist = c[0]
                selected = c

        if selected:
            sel_id = selected[3]
            sel_pos = selected[2]
            sel_of_var = selected[0]

            solution.insert_candidate(sol, sel_id, k, sel_pos, sel_of_var)

            if order == 'both':
                cl = update_candidate_list_linehauls_and_backhauls(sol, cl, sel_id, k)
            else:
                cl = update_candidate_list_first_linehauls(sol, cl, sel_id, k)

    return cl


def create_candidate_list_first_linehauls(sol):

    cl = []

    if sol['pending_linehauls']:

        for node_id in sol['pending_linehauls']:

            demand = sol['instance']['nodes'][node_id][3]

            for k in range(sol['instance']['l']):

                load = sol['delivery'][k]

                if demand + load > sol['instance']['q']:
                    continue

                for j in range(1, len(sol['routes'][k])):

                    prev_node_id = sol['routes'][k][j-1]
                    next_node_id = sol['routes'][k][j]

                    of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                                   sol['instance']['cost'][node_id][next_node_id] - \
                                   sol['instance']['cost'][prev_node_id][next_node_id], 2)

                    cl.append([of_var, k, j, node_id])

    elif sol['pending_backhauls']:

        for node_id in sol['pending_backhauls']:

            demand = sol['instance']['nodes'][node_id][3]

            for k in range(sol['instance']['l']):

                load = sol['pickup'][k]

                if demand + load > sol['instance']['q']:
                    continue

                for j in range(1, len(sol['routes'][k])):

                    next_node_id = sol['routes'][k][j]
                    next_node_type = sol['instance']['nodes'][next_node_id][0]

                    # El node següent no pot ser un linehaul
                    if next_node_type == 1:
                        continue

                    prev_node_id = sol['routes'][k][j-1]

                    of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                                   sol['instance']['cost'][node_id][next_node_id] - \
                                   sol['instance']['cost'][prev_node_id][next_node_id], 2)

                    cl.append([of_var, k, j, node_id])

    return cl


def create_candidate_list_linehauls_and_backhauls(sol):

    cl = []

    if sol['pending_linehauls']:

        for node_id in sol['pending_linehauls']:

            demand = sol['instance']['nodes'][node_id][3]

            for k in range(sol['instance']['l']):

                load = sol['delivery'][k]

                if demand + load > sol['instance']['q']:
                    continue

                for j in range(1, len(sol['routes'][k])):

                    prev_node_id = sol['routes'][k][j-1]
                    prev_node_type = sol['instance']['nodes'][prev_node_id][0]

                    if prev_node_type == 2:
                        break

                    next_node_id = sol['routes'][k][j]

                    of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                                   sol['instance']['cost'][node_id][next_node_id] - \
                                   sol['instance']['cost'][prev_node_id][next_node_id], 2)

                    cl.append([of_var, k, j, node_id])

    if sol['pending_backhauls']:

        for node_id in sol['pending_backhauls']:

            demand = sol['instance']['nodes'][node_id][3]

            for k in range(sol['instance']['l']):

                load = sol['pickup'][k]

                if demand + load > sol['instance']['q']:
                    continue

                for j in range(1, len(sol['routes'][k])):

                    next_node_id = sol['routes'][k][j]
                    next_node_type = sol['instance']['nodes'][next_node_id][0]

                    # El node següent no pot ser un linehaul
                    if next_node_type == 1:
                        continue

                    prev_node_id = sol['routes'][k][j-1]

                    of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                                   sol['instance']['cost'][node_id][next_node_id] - \
                                   sol['instance']['cost'][prev_node_id][next_node_id], 2)

                    cl.append([of_var, k, j, node_id])

    return cl


def update_candidate_list_first_linehauls(sol, cl, added_id, modified_k):

    # Es mantenen els candidats que no siguen el node que ja hem afegit ni la ruta que hem modificat
    new_cl = [c for c in cl if c[3] != added_id and c[1] != modified_k]

    if sol['pending_linehauls']:

        load = sol['delivery'][modified_k]

        for node_id in sol['pending_linehauls']:

            demand = sol['instance']['nodes'][node_id][3]

            if demand + load > sol['instance']['q']:
                continue

            # Recalculem les possibilitats que siguen factibles per a afegir a la ruta modificada
            for j in range(1, len(sol['routes'][modified_k])):

                prev_node_id, next_node_id = sol['routes'][modified_k][j - 1], sol['routes'][modified_k][j]

                of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                               sol['instance']['cost'][node_id][next_node_id] - \
                               sol['instance']['cost'][prev_node_id][next_node_id], 2)

                new_cl.append([of_var, modified_k, j, node_id])

    elif sol['pending_backhauls']:

        load = sol['pickup'][modified_k]

        for node_id in sol['pending_backhauls']:

            demand = sol['instance']['nodes'][node_id][3]

            if demand + load > sol['instance']['q']:
                continue

            for j in range(1, len(sol['routes'][modified_k])):

                next_node_id = sol['routes'][modified_k][j]
                next_node_type = sol['instance']['nodes'][next_node_id][0]

                if next_node_type == 1:
                    continue

                prev_node_id = sol['routes'][modified_k][j - 1]

                of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                               sol['instance']['cost'][node_id][next_node_id] - \
                               sol['instance']['cost'][prev_node_id][next_node_id], 2)

                new_cl.append([of_var, modified_k, j, node_id])

    return new_cl


def update_candidate_list_linehauls_and_backhauls(sol, cl, added_id, modified_k):

    # Es mantenen els candidats que no siguen el node que ja hem afegit ni la ruta que hem modificat
    new_cl = [c for c in cl if c[3] != added_id and c[1] != modified_k]

    if sol['pending_linehauls']:

        load = sol['delivery'][modified_k]

        for node_id in sol['pending_linehauls']:

            demand = sol['instance']['nodes'][node_id][3]

            if demand + load > sol['instance']['q']:
                continue

            # Recalculem les possibilitats que siguen factibles per a afegir a la ruta modificada
            for j in range(1, len(sol['routes'][modified_k])):

                prev_node_id = sol['routes'][modified_k][j - 1]
                prev_node_type = sol['instance']['nodes'][prev_node_id][0]

                if prev_node_type == 2:
                    break

                next_node_id = sol['routes'][modified_k][j]

                of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                               sol['instance']['cost'][node_id][next_node_id] - \
                               sol['instance']['cost'][prev_node_id][next_node_id], 2)

                new_cl.append([of_var, modified_k, j, node_id])

    if sol['pending_backhauls']:

        load = sol['pickup'][modified_k]

        for node_id in sol['pending_backhauls']:

            demand = sol['instance']['nodes'][node_id][3]

            if demand + load > sol['instance']['q']:
                continue

            for j in range(1, len(sol['routes'][modified_k])):

                next_node_id = sol['routes'][modified_k][j]
                next_node_type = sol['instance']['nodes'][next_node_id][0]

                if next_node_type == 1:
                    continue

                prev_node_id = sol['routes'][modified_k][j - 1]

                of_var = round(sol['instance']['cost'][prev_node_id][node_id] + \
                               sol['instance']['cost'][node_id][next_node_id] - \
                               sol['instance']['cost'][prev_node_id][next_node_id], 2)

                new_cl.append([of_var, modified_k, j, node_id])

    return new_cl