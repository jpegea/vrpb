import math

def read_instance(path):
    """
    Llig una instància amb el format indicat

    Parameters
    ----------
    path : string
        Ruta del fitxer

    Returns
    -------
    mat : dict
        Diccionari amb la informació de la instància i el càlcul de distàncies entre nodes.
    """

    instance = {}

    file_format = 'gj'
    if '/TV/' in path:
        file_format = 'tv'

    with open(path, 'r') as f:
        next(f)  # Descarta la primera línia
        _, _, x, y, _, q, l, n, m = f.readline().split(',')

        n = int(n)
        m = int(m)

        instance['q'] = int(q)
        instance['l'] = int(l)
        instance['n'] = n
        instance['m'] = m

        instance['nodes'] = [[]*4 for _ in range(n+m+1)]
        instance['cost'] = [[0]*(n+m+1) for _ in range(n+m+1)]

        instance['linehauls'] = [[0]*4 for _ in range(n)]
        instance['backhauls'] = [[0]*4 for _ in range(m)]

        instance['nodes'][0] = [0, 0, (int(x), int(y)), 0]

        idx_l = 0  # Índex per als nodes del linehaul
        idx_b = 0  # Índex per als nodes del backhaul

        for i in range(n+m):
            node_type, node_id, x, y, demand, _, _, _, _ = f.readline().split(',')

            if file_format == 'tv':
                node_type, node_id = int(node_id) + 1, int(node_type) - 1
            else:
                node_type = int(node_type)
                node_id = int(node_id)

            instance['nodes'][node_id] = [node_type, node_id, (int(x), int(y)), int(demand)]

            if int(node_type) == 1:
                instance['linehauls'][idx_l] = instance['nodes'][node_id][1]
                idx_l += 1

            if int(node_type) == 2:
                instance['backhauls'][idx_b] = instance['nodes'][node_id][1]
                idx_b += 1

            for j in range(i+1):
                dist = math.dist(instance['nodes'][i+1][2], instance['nodes'][j][2])
                instance['cost'][i+1][j] = round(dist, 2)
                instance['cost'][j][i+1] = round(dist, 2)

    return instance


def export_ampl(inst):
    print('data;\n')

    print(f"param n := {inst['n']};")
    print(f"param m := {inst['m']};")
    print(f"param l := {inst['l']};")
    print(f"param q := {inst['q']};\n")

    print(f'param d :=')
    for node_id in inst['linehauls']:
        node = inst['nodes'][node_id]
        print(node[1], end='\t')
        print(node[3], end=(';\n' if node[1] == inst['linehauls'][-1] else '\n'))
    print()

    print(f'param p :=')
    for node_id in inst['backhauls']:
        node = inst['nodes'][node_id]
        print(node[1], end='\t')
        print(node[3], end=(';\n' if node[1] == inst['backhauls'][-1] else '\n'))
    print()

    print(f'param c :')
    for i in range(inst['n'] + inst['m'] + 1):
        print(f'\t{i}', end='')
    print(' :=')
    for i in range(inst['n'] + inst['m'] + 1):
        print(i, end='\t')
        for j in range(inst['n'] + inst['m'] + 1):
            print(inst['cost'][i][j], end='\t')

        if i == inst['n'] + inst['m']:
            print(';')
        else:
            print()
