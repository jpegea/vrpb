import matplotlib.pyplot as plt

def create_empty_solution(instance: dict):

    sol = {
        'instance': instance,
        'routes': [[0, 0] for _ in range(instance['l'])],
        'delivery' : [0] * instance['l'],
        'pickup' : [0] * instance['l'],
        'pending_linehauls' : instance['linehauls'].copy(),
        'pending_backhauls': instance['backhauls'].copy(),
        'of': 0.0,
        'feasible': False
    }

    return sol


def insert_candidate(solution: dict, candidate: tuple[float, int, int, int]):

    of_var, k, pos, node_id = candidate

    nodes = solution['instance']['nodes']
    route = solution['routes'][k]

    node_data = nodes[node_id]
    node_type = node_data[0]

    # Elimina el node de la llista d'elements pendents d'entrega o recollida

    pending = solution['pending_linehauls' if node_type == 1 else 'pending_backhauls']

    pending.remove(node_id)

    # Insereix el node

    route.insert(pos, node_id)

    # Actualitza el cost de la solució

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)

    # Actualitza la càrrega de la ruta

    if node_type == 1:
        load = solution['delivery']
    else:
        load = solution['pickup']

    node_demand = node_data[3]
    load[k] += node_demand


def do_intra_shift(solution: dict, k: int, sel_nodes: tuple[int, int], of_var: float):

    i, j = sel_nodes
    route = solution['routes'][k]

    node_id = route.pop(i)
    if i > j:
        route.insert(j + 1, node_id)
    else:
        route.insert(j, node_id)

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)


def do_intra_swap(solution: dict, k: int, sel_nodes: tuple[int, int], of_var: float):

    i, j = sel_nodes
    route = solution['routes'][k]

    route[i], route[j] = route[j], route[i]

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)


def do_intra_2opt(solution: dict, k: int, sel_nodes: tuple[int, int], of_var: float):

    i, j = sel_nodes
    route = solution['routes'][k]

    route[i:j+1] = reversed(route[i:j+1])

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)


def do_inter_shift(solution: dict, sel_routes: tuple[int, int], sel_nodes: tuple[int, int], of_var: float):

    nodes = solution['instance']['nodes']

    k, l = sel_routes
    i, j = sel_nodes

    route_k = solution['routes'][k]
    route_l = solution['routes'][l]

    # Realitza la inserció

    node_id = route_k.pop(i)
    route_l.insert(j + 1, node_id)

    # Actualitza of

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)

    # Actualitza la càrrega

    node_data = nodes[node_id]
    node_type = node_data[0]
    node_demand = node_data[3]

    if node_type == 1:
        load = solution['delivery']
    else:
        load = solution['pickup']

    load[k] -= node_demand
    load[l] += node_demand


def do_inter_swap(solution: dict, sel_routes: tuple[int, int], sel_nodes: tuple[int, int], of_var: float):

    nodes = solution['instance']['nodes']

    k, l = sel_routes
    i, j = sel_nodes

    route_k = solution['routes'][k]
    route_l = solution['routes'][l]

    i_id = route_k[i]
    j_id = route_l[j]

    # Realitza el swap

    route_k[i], route_l[j] = j_id, i_id

    # Actualitza of

    of = solution['of']
    of += of_var
    solution['of'] = round(of, 2)

    # Actualitza la càrrega

    i_data = nodes[i_id]
    i_type = i_data[0]
    i_demand = i_data[3]

    if i_type == 1:
        load_i = solution['delivery']
    else:
        load_i = solution['pickup']

    load_i[k] -= i_demand
    load_i[l] += i_demand

    j_data = nodes[j_id]
    j_type = j_data[0]
    j_demand = j_data[3]

    if j_type == 1:
        load_j = solution['delivery']
    else:
        load_j = solution['pickup']

    load_j[l] -= j_demand
    load_j[k] += j_demand


def evaluate(solution: dict):

    cost = solution['instance']['cost']

    dist = 0.0

    for route in solution['routes']:
        prev_node_id = 0
        for node_id in route[1:]:
            dist += cost[prev_node_id][node_id]
            prev_node_id = node_id

    return round(dist, 2)


def check_feasibility(solution: dict):

    feasible = True

    if solution['pending_linehauls'] or solution['pending_backhauls']:
        feasible = False
        print("NODES NO VISITATS")

    for k in range(solution['instance']['l']):

        route = solution['routes'][k]

        if route[0] != 0 or route[-1] != 0:
            feasible = False
            print(f"RUTA {k} NO COMENÇA I ACABA EN DEPÒSIT")

        delivery_demand = 0
        pickup_demand = 0

        for i in range(1, len(route) - 1):

            node_type = solution['instance']['nodes'][route[i]][0]
            prev_node_type = solution['instance']['nodes'][route[i - 1]][0]

            if node_type == 1 and prev_node_type == 2:
                feasible = False
                print("RECOLLIDA ABANS D'ENTREGA")

            if solution['instance']['nodes'][route[i]][0] == 1:
                delivery_demand += solution['instance']['nodes'][route[i]][3]

            elif solution['instance']['nodes'][route[i]][0] == 2:
                pickup_demand += solution['instance']['nodes'][route[i]][3]

            else:
                feasible = False
                print(f"NODE {i} DE LA RUTA {k} NO ÉS ENTREGA NI RECOLLIDA")

            if delivery_demand > solution['instance']['q']:
                feasible = False
                print("CAPACITAT D'ENTREGUES SUPERADA")

            if pickup_demand > solution['instance']['q']:
                feasible = False
                print("CAPACITAT DE RECOLLIDES SUPERADA")

        if solution['feasible'] != feasible or solution['of'] != evaluate(solution):
            print("ERROR GARRAFAL")

    return feasible


def print_solution(solution: dict):

    l = solution['instance']['l']
    routes = solution['routes']

    print('\nSolució:')

    for k in range(l):
        route = routes[k]
        print(f'Vehicle {k} -> 0', end='')
        for node_id in route[1:-1]:
            print(node_id, end=' -- ')
        print('0')

    print()


def draw_solution(solution: dict, fig_size: tuple=None, b: bool=True, t: str=None, save_fig: str=None,
                  show_legend: bool=True):

    nodes = solution['instance']['nodes']

    # Figura i eixos
    fig, ax = plt.subplots(figsize=fig_size)

    ax.set_aspect('equal')

    # Dibuixa depòsit
    depot = nodes[0]
    ax.scatter(depot[2][0], depot[2][1], marker='s', c="black", s=30, zorder=3, label="Depòsit", rasterized=True)

    # Dibuixar linehaul
    linehauls = solution['instance']['linehauls']
    lx = [nodes[nl][2][0] for nl in linehauls]
    ly = [nodes[nl][2][1] for nl in linehauls]
    ax.scatter(lx, ly, marker='o', c="black", s=20, zorder=3, label="Linehaul", rasterized=True)

    # Dibuixar backhaul
    backhauls = solution['instance']['backhauls']
    bx = [nodes[nb][2][0] for nb in backhauls]
    by = [nodes[nb][2][1] for nb in backhauls]
    ax.scatter(bx, by, marker='^', c="black", s=20, zorder=3, label="Backhaul", rasterized=True)

    # Dibuixa cada ruta
    for k in range(solution['instance']['l']):
        rout = solution['routes'][k]
        rx = [nodes[i][2][0] for i in rout]
        ry = [nodes[i][2][1] for i in rout]
        plt.plot(rx, ry, label="Vehicle " + str(k+1), linewidth=1.2, zorder=2, rasterized=True)

    if t:
        plt.title(t + f", of: ${solution['of']}$", fontsize=12)
    else:
        plt.title(f"of: ${solution['of']}$", fontsize=12)

    # ax.tick_params(axis='both', which='major', labelsize=8)
    ax.axis('off')
    if show_legend:
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, 0),
            ncol=4,
            fontsize=10,
            frameon=False
        )

    plt.tight_layout()

    if save_fig:
        plt.savefig(save_fig + '.pdf', format="pdf", bbox_inches="tight", dpi=300)

    plt.show(block=b)
    plt.pause(0.1)
    plt.pause(0.1)