from constructives import cgrasp
from localsearch import ls_full, ls_neighbors
from structure import instance
import statistics, time


def execute_full_ls(inst: dict, time_limit: float, alpha: float, strategy: str='best', first_in_construction: str='linehauls'):

    best = {}
    iters = 0

    start = time.time()

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta=0, first=first_in_construction)

        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters

            sol = cgrasp.construct(inst, alpha, beta=0, first=first_in_construction)

        iters += 1

        ls_full.improve_routes(sol, strategy)
        ls_full.improve_inter_route(sol, strategy)

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters


def execute_ensuring_feasibility(inst: dict, time_limit: float, alpha: float, max_not_feasible_ratio: float=.9,
                                 strategy: str='best', first_in_construction: str='linehauls'):

    best = {}
    iters = 0

    beta = 0
    n_created_sols = 0
    not_feasible_sols = 0

    start = time.time()

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta, first=first_in_construction)
        n_created_sols += 1
        feasibility_checked = 1

        while not sol['feasible']:
            not_feasible_sols += 1

            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters

            sol = cgrasp.construct(inst, alpha, beta, first=first_in_construction)
            n_created_sols += 1

            if n_created_sols <= 5 * feasibility_checked:
                if not_feasible_sols / n_created_sols > max_not_feasible_ratio and beta < 1:
                    beta += .05
                    beta = round(beta, 2)
                elif not_feasible_sols / n_created_sols < max_not_feasible_ratio and beta > 0:
                    beta -= .01
                    beta = round(beta, 2)
                feasibility_checked += 1

        iters += 1

        print(f'Sol {iters}: {sol['of']}')

        ls_full.improve_routes(sol, strategy)
        ls_full.improve_inter_route(sol, strategy)

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters


def execute_smart_ls(inst: dict, time_limit: float, alpha: float, strategy: str='best', first_in_construction: str='linehauls'):

    neighbors = instance.eval_k_neighbors(inst, 15)

    best = {}
    iters = 0

    start = time.time()

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta=0, first=first_in_construction)

        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters

            sol = cgrasp.construct(inst, alpha, beta=0, first=first_in_construction)

        iters += 1

        ls_full.improve_routes(sol, strategy)
        ls_neighbors.improve_inter_route(sol, neighbors, strategy)

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters


"""
def execute2(inst, time_limit, alpha, strategy='best', sample_size=10):

    first_in_construction = 'both'

    best = {}
    improvements = [0] * sample_size

    start = time.time()

    for i in range(10):

        sol = cgrasp.construct(inst, alpha, first=first_in_construction)

        # 1er entorn
        ls_full_check.improve_routes(sol, strategy)

        of_before = sol['of']

        # 2n entorn
        ls_full_check.combine_routes(sol, strategy)
        of_after = sol['of']

        improvements[i] = 1 - of_after / of_before
        print(improvements[i])
        if not best or of_after < best['of']:
            best = sol

    mean = statistics.mean(improvements)
    sd = statistics.stdev(improvements)

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, first=first_in_construction)

        ls_full_check.improve_routes(sol, strategy)
        of_before = sol['of']

        gap_to_best = 1 - best['of'] / of_before
        if gap_to_best > mean + 2 * sd:
            continue

        ls_full_check.combine_routes(sol, strategy)
        of_after = sol['of']

        if of_after < best['of']:
            best = sol

        imp = 1 - of_after / of_before
        improvements.append(imp)
        mean = statistics.mean(improvements)
        sd = statistics.stdev(improvements)

    return best
"""