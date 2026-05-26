from constructives import cgreedy

def execute(inst):
    sol = cgreedy.construct(inst, 0, 'both')
    return sol