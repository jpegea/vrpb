from constructives import cgreedy

def execute(inst):
    sol = cgreedy.construct(inst, 'both')
    return sol