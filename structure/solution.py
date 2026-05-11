import matplotlib.pyplot as plt


def create_empty_solution(instance):
    """Crea una solució buida"""

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


def insert_candidate(solution, node_id, k, pos, of_variation):
    """Insereix el node en la ruta del vehicle indicat"""

    # Elimina el node de la llista d'elements pendents d'entrega o recollida
    node_type = solution['instance']['nodes'][node_id][0]
    pending = solution['pending_linehauls' if node_type == 1 else 'pending_backhauls']
    for i in range(len(pending)):
        if pending[i] == node_id:
            pending.pop(i)
            break

    # Insereix el node
    solution['routes'][k].insert(pos, node_id)

    # Actualitza el cost de la solució
    solution['of'] += of_variation
    solution['of'] = round(solution['of'], 2)

    # Actualitza la càrrega de la ruta
    solution['delivery' if node_type == 1 else 'pickup'][k] += solution['instance']['nodes'][node_id][3]


def do_intra_shift(solution, k, sel_nodes, of_var):
    i, j = sel_nodes
    route = solution['routes'][k]

    node_id = route.pop(i)
    if i > j:
        route.insert(j + 1, node_id)
    else:
        route.insert(j, node_id)

    solution['of'] += of_var
    solution['of'] = round(solution['of'], 2)


def do_intra_swap(solution, k, sel_nodes, of_var):
    i, j = sel_nodes
    route = solution['routes'][k]

    route[i], route[j] = route[j], route[i]

    solution['of'] += of_var
    solution['of'] = round(solution['of'], 2)


def do_intra_2opt(solution, k, sel_nodes, of_var):
    i, j = sel_nodes
    route = solution['routes'][k]

    left = i
    right = j
    while left < right:
        route[left], route[right] = route[right], route[left]
        left += 1
        right -= 1

    solution['of'] += of_var
    solution['of'] = round(solution['of'], 2)


def do_inter_shift(solution, sel_routes, sel_nodes, of_var):
    k, l = sel_routes
    i, j = sel_nodes

    # Realitza la inserció
    n_id = solution['routes'][k].pop(i)
    solution['routes'][l].insert(j + 1, n_id)

    # Actualitza of
    solution['of'] += of_var
    solution['of'] = round(solution['of'], 2)

    # Actualitza la càrrega
    node_type, demand = solution['instance']['nodes'][n_id][0], solution['instance']['nodes'][n_id][3]
    solution['delivery' if node_type == 1 else 'pickup'][k] -= demand
    solution['delivery' if node_type == 1 else 'pickup'][l] += demand


def do_inter_swap(solution, sel_routes, sel_nodes, of_var):
    k, l = sel_routes
    i, j = sel_nodes

    nk_id = solution['routes'][k][i]
    nl_id = solution['routes'][l][j]

    # Realitza el swap
    solution['routes'][l][j], solution['routes'][k][i] = nk_id, nl_id

    # Actualitza of
    solution['of'] += of_var
    solution['of'] = round(solution['of'], 2)

    # Actualitza la càrrega
    node_type_k, node_type_l = solution['instance']['nodes'][nk_id][0], solution['instance']['nodes'][nl_id][0]
    demand_k, demand_l = solution['instance']['nodes'][nk_id][3], solution['instance']['nodes'][nl_id][3]

    solution['delivery' if node_type_k == 1 else 'pickup'][k] -= demand_k
    solution['delivery' if node_type_k == 1 else 'pickup'][l] += demand_k

    solution['delivery' if node_type_l == 1 else 'pickup'][k] += demand_l
    solution['delivery' if node_type_l == 1 else 'pickup'][l] -= demand_l


def evaluate(solution):
    """Calcula el cost total d'una solució"""

    cost = 0.0

    for rout in solution['routes']:
        for i in range(1, len(rout)):
            cost += solution['instance']['cost'][rout[i-1]][rout[i]]

    return round(cost, 2)


def check_feasibility(solution):

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


def print_solution(solution):
    """Imprimeix la solució"""

    print("\nSolució:")
    for k in range(solution['instance']['l']):
        print("Vehicle", k, "->", end="\t")
        for i in range(len(solution['routes'][k])):
            print(solution['routes'][k][i], end=" -- " if i < len(solution['routes'][k])-1 else "\n")
    print()


def draw_solution(solution, b=True, t=''):
    """Gráfica de la solució"""

    # Figura i eixos
    fig, ax = plt.subplots(figsize=(5.5, 4))

    # Dibuixa depòsit
    depot = solution['instance']['nodes'][0]
    ax.scatter(depot[2][0], depot[2][1], marker='s', c="black", s=30, zorder=3, label="Depòsit")

    # Dibuixar linehaul
    linehauls = solution['instance']['linehauls']
    lx = [solution['instance']['nodes'][nl][2][0] for nl in linehauls]
    ly = [solution['instance']['nodes'][nl][2][1] for nl in linehauls]
    ax.scatter(lx, ly, marker='o', c="black", s=20, zorder=3, label="Linehaul")

    # Dibuixar backhaul
    backhauls = solution['instance']['backhauls']
    bx = [solution['instance']['nodes'][nb][2][0] for nb in backhauls]
    by = [solution['instance']['nodes'][nb][2][1] for nb in backhauls]
    ax.scatter(bx, by, marker='^', c="black", s=20, zorder=3, label="Backhaul")

    # Dibuixa cada ruta
    for k in range(solution['instance']['l']):
        rout = solution['routes'][k]
        rx = [solution['instance']['nodes'][i][2][0] for i in rout]
        ry = [solution['instance']['nodes'][i][2][1] for i in rout]
        plt.plot(rx, ry, label="Vehicle " + str(k+1), linewidth=1, zorder=2)

    if t:
        plt.title(t + f", of: ${solution['of']}$", fontsize=12)
    else:
        plt.title(f"of: ${solution['of']}$", fontsize=12)

    # ax.tick_params(axis='both', which='major', labelsize=8)
    ax.axis('off')
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.12),
        ncol=4,
        fontsize=10,
        frameon=False
    )

    plt.tight_layout()

    plt.show(block=b)