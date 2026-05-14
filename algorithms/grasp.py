from constructives import cgrasp
from localsearch import ls_full_check
import statistics

def execute(inst, iters, alpha, strategy='best'):

    first_in_construction = 'both'

    best = {}

    for i in range(iters):

        print('Iter ' + str(i + 1) + ': ', end='')

        sol = cgrasp.construct(inst, alpha, first=first_in_construction)

        print('C -> ' + str(sol['of']), end=', ')

        ls_full_check.improve_routes(sol, strategy)
        ls_full_check.combine_routes(sol, strategy)

        print('LS -> ' + str(sol['of']))

        if not best or sol['of'] < best['of']:
            best = sol

    return best
        if strategy == 'best':
            lsbestimp.improve(sol)
        else:
            lsfirstimp.improve(sol)
        print('LS -> ' + str(sol['of']))
        if best is None or sol['of'] < best['of']:
            best = sol
    return best