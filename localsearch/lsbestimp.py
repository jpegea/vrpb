from localsearch import intra_route, inter_route


def improve(sol, show_operations=False):
    improvement = True
    while improvement:
        vnd_intra(sol, show_operations)
        improvement = vnd_inter(sol)


def vnd_intra(sol, show_operations=False):
    improvement = False
    for k in range(sol['instance']['l']):
        imp_route = True
        while imp_route:
            imp_route = intra_route.shift(sol, k, 'best')
            if imp_route:
                if show_operations:
                    print("Intra: Shift")
                improvement = True
            if not imp_route:
                imp_route = intra_route.swap(sol, k, 'best')
                if imp_route:
                    if show_operations:
                        print("Intra: Swap")
                    improvement = True
            if not imp_route:
                imp_route = intra_route.two_opt(sol, k, 'best')
                if imp_route:
                    if show_operations:
                        print("Intra: 2-opt")
                    improvement = True
    return improvement


def vnd_inter(sol, show_operations=False):
    improvement = False
    imp = True
    while imp:
        imp = inter_route.shift(sol, 'best')
        if imp:
            if show_operations:
                print("Inter: Shift")
            improvement = True
        if not imp:
            imp = inter_route.swap(sol, 'best')
            if imp:
                if show_operations:
                    print("Inter: Swap")
                improvement = True

    return improvement