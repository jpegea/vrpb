from constructives import cgreedy

def execute(inst):
    sol = cgreedy.construct(inst, 0, 'linehauls')
    return sol

def execute_with_initial_nodes(inst, priority='distance'):
    sol = cgreedy.construct_with_initial_nodes(inst, 0, 'linehauls', priority)
    return sol