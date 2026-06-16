from constructives import cgrasp
from localsearch import ls_full, ls_neighbors
from structure import instance
import math, time
from collections import deque


def execute(inst: dict, time_limit: float, alpha: float):

    best = {}
    iters = 0

    start = time.time()

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta=0)
        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters
            sol = cgrasp.construct(inst, alpha, beta=0)

        iters += 1

        ls_full.vnd(sol, 'first', 'first')

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters


def execute_ensuring_feasibility(inst: dict, time_limit: float, alpha: float):

    best = {}
    iters = 0

    start = time.time()

    max_ratio = .9
    beta = 0
    kp = 0.7
    kd = 0.4
    prev_error = 0.0
    history = deque(maxlen=30)
    n_created_sols = 0

    while time.time() - start < time_limit:

        # Fase constructiva

        sol = cgrasp.construct(inst, alpha, beta)
        n_created_sols += 1
        history.append(1 if not sol['feasible'] else 0)
        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters
            sol = cgrasp.construct(inst, alpha, beta)
            n_created_sols += 1
            history.append(1 if not sol['feasible'] else 0)
            if n_created_sols % 10 == 0:
                current_ratio = sum(history) / len(history)
                error = current_ratio - max_ratio
                prop = kp * error
                der = kd * (error - prev_error)
                delta_beta = prop + der
                beta = max(0.0, min(1.0, beta + delta_beta))
                prev_error = error

        iters += 1

        # Fase de cerca local

        ls_full.vnd(sol)

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters


def execute_filtering(inst: dict, time_limit: float, alpha: int, sample_size: int=10):

    best = {}
    
    count = 0.0
    mean = 0.0
    m2 = 0.0

    l = inst['l']

    start = time.time()

    for i in range(sample_size):

        sol = cgrasp.construct(inst, alpha, beta=0)
        while not sol['feasible']:
            sol = cgrasp.construct(inst, alpha, beta=0)

        # 1er entorn

        for k in range(l):
            ls_full.improve_route(sol, k, 'first')
            
        of_before = sol['of']

        # 2n entorn
        
        improvement = True
        while improvement:
            improvement = ls_full.inter_swap(sol, 'first', 'first')
            if not improvement:
                improvement = ls_full.inter_shift(sol, 'first', 'first')

        of_after = sol['of']

        imp = 1 - of_after / of_before
        
        count += 1
        delta = imp - mean
        mean += delta / count
        delta2 = imp - mean
        m2 += delta * delta2

        if not best or of_after < best['of']:
            best = sol

    variance = m2 / (count - 1) if count > 1 else 0.0
    sd = math.sqrt(variance)
    iters = sample_size

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta=0)
        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters
            sol = cgrasp.construct(inst, alpha, beta=0)

        for k in range(l):
            ls_full.improve_route(sol, k, 'first')

        of_before = sol['of']

        gap_to_best = 1 - best['of'] / of_before
        if gap_to_best > mean + 2 * sd:
            continue

        improvement = True
        while improvement:
            improvement = ls_full.inter_swap(sol, 'first', 'first')
            if not improvement:
                improvement = ls_full.inter_shift(sol, 'first', 'first')
        
        of_after = sol['of']

        if of_after < best['of']:
            best = sol

        imp = 1 - (of_after / of_before)
        
        count += 1
        delta = imp - mean
        mean += delta / count
        delta2 = imp - mean
        m2 += delta * delta2
        
        variance = m2 / (count - 1) if count > 1 else 0.0
        sd = math.sqrt(variance)

        iters += 1

    return best, iters


def execute_k_neightbors(inst: dict, time_limit: float, alpha: float):

    neighbors = instance.eval_k_neighbors(inst, 15)

    best = {}
    iters = 0

    start = time.time()

    while time.time() - start < time_limit:

        sol = cgrasp.construct(inst, alpha, beta=0)

        while not sol['feasible']:
            if time.time() - start > time_limit:
                if not best:
                    best = sol
                return best, iters

            sol = cgrasp.construct(inst, alpha, beta=0)

        iters += 1

        # ls_neighbors.improve_inter_route(sol, neighbors, strategy)

        if not best or sol['of'] < best['of']:
            best = sol

    return best, iters