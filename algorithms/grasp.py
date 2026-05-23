from constructives import cgrasp
from localsearch import ls_full_check
import statistics, time

def execute(inst, time_limit, alpha, strategy='best'):

    first_in_construction = 'both'

    best = {}

    start = time.time()
    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, first=first_in_construction)
        while not sol['feasible'] and time.time() - start < time_limit:
            sol = cgrasp.construct(inst, alpha, first=first_in_construction)

        ls_full_check.improve_routes(sol, strategy)
        ls_full_check.combine_routes(sol, strategy)

        if not best or sol['of'] < best['of']:
            best = sol

    return best


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
        if not best or of_after < best['of']:
            best = sol

    mean = statistics.mean(improvements)
    sd = statistics.stdev(improvements)

    print(f"M: {mean} \t S: {sd}")

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

        improvements.append(1 - of_after / of_before)
        mean = statistics.mean(improvements)
        sd = statistics.stdev(improvements)
        print(f"M: {mean} \t S: {sd}")
        print(f"M: {mean} \t S: {sd}")

    return best