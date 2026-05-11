from constructives import cgrasp
from localsearch import lsbestimp, lsfirstimp

def execute(inst, iters, alpha, strategy='best'):
    best = None
    for i in range(iters):
        print('Iter ' + str(i + 1) + ': ', end='')
        sol = cgrasp.construct(inst, alpha, 'both')
        print('C -> ' + str(sol['of']), end=', ')
        if strategy == 'best':
            lsbestimp.improve(sol)
        else:
            lsfirstimp.improve(sol)
        print('LS -> ' + str(sol['of']))
        if best is None or sol['of'] < best['of']:
            best = sol
    return best