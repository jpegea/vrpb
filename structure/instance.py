import math

def read_instance(path):

    instance = {}

    file_format = 'tv'

    with open(path, 'r') as f:
        first_word, _, _, _, _, _, _, _, _ = f.readline().split(',')

        if first_word == 'type':
            file_format = 'gj'

        _, _, x, y, _, q, l, n, m = f.readline().split(',')

        n = int(n)
        m = int(m)

        n_clients = n + m

        instance['q'] = int(q)
        instance['l'] = int(l)
        instance['n'] = n
        instance['m'] = m

        instance['nodes'] = [[0]*4 for _ in range(n+m+1)]
        instance['cost'] = [[0]*(n+m+1) for _ in range(n+m+1)]

        instance['linehauls'] = set()
        instance['backhauls'] = set()

        nodes = instance['nodes']
        linehauls = instance['linehauls']
        backhauls = instance['backhauls']

        nodes[0] = [0, 0, (int(x), int(y)), 0]

        for _ in range(n_clients):
            node_type, node_id, x, y, demand, _, _, _, _ = f.readline().split(',')

            if file_format == 'tv':
                node_type, node_id = int(node_id) + 1, int(node_type) - 1
            else:
                node_type = int(node_type)
                node_id = int(node_id)

            nodes[node_id] = [node_type, node_id, (int(x), int(y)), int(demand)]

            if node_type == 1:
                linehauls.add(node_id)

            if node_type == 2:
                backhauls.add(node_id)

        cost = instance['cost']

        for i in range(n_clients + 1):

            i_data = nodes[i]
            i_pos = i_data[2]

            for j in range(n_clients + 1):

                if i == j:
                    continue

                j_data = nodes[j]
                j_pos = j_data[2]

                dist = math.dist(i_pos, j_pos)

                cost[i][j] = round(dist, 2)
                cost[j][i] = round(dist, 2)

    return instance


def eval_k_neighbors(inst: dict, k: int):

    cost = inst['cost']
    n_clients = inst['n']

    k_neighbors = {}

    for i in range(1, n_clients + 1):

        distances = []

        for j in range(1, n_clients + 1):
            if i == j:
                continue
            distances.append((cost[i][j], j))

        distances.sort(key=lambda x: x[0])

        k_neighbors[i] = set([j for _, j in distances[:k]])

    return k_neighbors


def export_ampl(inst: dict):

    n = inst['n']
    m = inst['m']

    print('data;\n')

    print(f"param n := {n};")
    print(f"param m := {m};")
    print(f"param l := {inst['l']};")
    print(f"param q := {inst['q']};\n")

    nodes = inst['nodes']
    linehauls = inst['linehauls']
    backhauls = inst['backhauls']

    # Demanda de linehauls

    print(f'param d :=', end='')

    for node_id in linehauls:

        node_data = nodes[node_id]
        node_demand = node_data[3]

        print(f'\n{node_id}\t{node_demand}', end='')

    print(';\n')

    # Demanda de backhauls

    print(f'param p :=', end='')

    for node_id in backhauls:

        node_data = nodes[node_id]
        node_demand = node_data[3]

        print(f'\n{node_id}\t{node_demand}', end='')

    print(';\n')

    cost = inst['cost']

    print(f'param c :')
    for i in range(n+m+1):
        print(f'\t{i}', end='')
    print(' :=', end='')

    for i in range(n+m+1):
        print(f'\n{i}', end='')
        for j in range(n+m+1):
            print(f'\t{cost[i][j]}', end='')
    print(';\n')
