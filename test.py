from pathlib import Path
from constructives import cgreedy, cgrasp
from algorithms import greedy
from structure import instance
import csv, random

def execute_test_greedy_both_vs_linehauls():
    ruta_tv = Path('instances/TV')
    ruta_gj = Path('instances/GJ')
    instancies = list(ruta_tv.glob('*.csv')) + list(ruta_gj.glob('*.csv'))
    if not instancies:
        print("No s'ha trobat cap instància")
        return

    f_resultats = 'results/greedy_both_vs_linehauls.csv'
    existeix_fitxer = Path(f_resultats).exists()
    with open(f_resultats, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existeix_fitxer:
            writer.writerow(['Inst', 'First', 'Feasible', 'Of'])
        else:
            print('Ja existeix un fitxer amb els resultats')
            return

        for n in range(len(instancies)):
            f_inst = instancies[n]
            inst = instance.read_instance(f_inst)
            for estrategia in ['linehauls', 'both']:
                print(f'Inst {n+1}/{len(instancies)}: {f_inst} | Construcció: {estrategia}')
                sol = cgreedy.construct(inst, 0, estrategia)
                writer.writerow([f_inst, estrategia, sol['feasible'], sol['of']])
                f.flush()

    print('Experiment finalitzat amb èxit')


def execute_test_greedy_initial_separation():
    ruta_tv = Path('instances/TV')
    ruta_gj = Path('instances/GJ')
    instancies = list(ruta_tv.glob('*.csv')) + list(ruta_gj.glob('*.csv'))
    if not instancies:
        print("No s'ha trobat cap instància")
        return

    f_resultats = 'results/greedy_initial_separation.csv'
    existeix_fitxer = Path(f_resultats).exists()

    with open(f_resultats, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existeix_fitxer:
            writer.writerow(['Inst', 'Initial', 'Feasible', 'Of'])
        else:
            print('Ja existeix un fitxer amb els resultats')
            return

        for n in range(len(instancies)):
            f_inst = instancies[n]
            inst = instance.read_instance(f_inst)
            print(f'Inst {n+1}/{len(instancies)}: {f_inst} | Sense nodes inicials')
            sol = greedy.execute(inst)
            writer.writerow([f_inst, False, sol['feasible'], sol['of']])
            f.flush()
            print(f'Inst {n + 1}/{len(instancies)}: {f_inst} | Amb nodes inicials')
            sol = greedy.execute_with_initial_nodes(inst, priority='distance')
            writer.writerow([f_inst, True, sol['feasible'], sol['of']])
            f.flush()

    print('Experiment finalitzat amb èxit')


def execute_test_greedy_initial_demand_priority():
    ruta_tv = Path('instances/TV')
    ruta_gj = Path('instances/GJ')
    instancies = list(ruta_tv.glob('*.csv')) + list(ruta_gj.glob('*.csv'))
    if not instancies:
        print("No s'ha trobat cap instància")
        return

    f_resultats = 'results/greedy_initial_demand_priority.csv'
    existeix_fitxer = Path(f_resultats).exists()

    with open(f_resultats, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existeix_fitxer:
            writer.writerow(['Inst', 'Initial', 'Feasible', 'Of'])
        else:
            print('Ja existeix un fitxer amb els resultats')
            return

        for n in range(len(instancies)):
            f_inst = instancies[n]
            inst = instance.read_instance(f_inst)
            print(f'Inst {n+1}/{len(instancies)}: {f_inst} | Sense nodes inicials')
            sol = greedy.execute(inst)
            writer.writerow([f_inst, False, sol['feasible'], sol['of']])
            f.flush()
            print(f'Inst {n + 1}/{len(instancies)}: {f_inst} | Amb nodes inicials')
            sol = greedy.execute_with_initial_nodes(inst, priority='demand')
            writer.writerow([f_inst, True, sol['feasible'], sol['of']])
            f.flush()

    print('Experiment finalitzat amb èxit')


def execute_test_grasp_alpha_constructive_sequential_w_and_wo_initial_nodes():
    ruta_tv = Path('instances/TV')
    ruta_gj = Path('instances/GJ')
    instancies = list(ruta_tv.glob('*.csv')) + list(ruta_gj.glob('*.csv'))
    if not instancies:
        print("No s'ha trobat cap instància")
        return

    f_resultats = 'results/grasp_alpha_constructive_sequential_w_and_wo_initial_nodes.csv'
    existeix_fitxer = Path(f_resultats).exists()

    with open(f_resultats, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existeix_fitxer:
            writer.writerow(['Inst', 'Seed', 'Alpha', 'InitialNodes', 'Feasible', 'Of'])
        else:
            print('Ja existeix un fitxer amb els resultats')
            return

        for n in range(len(instancies)):
            f_inst = instancies[n]
            inst = instance.read_instance(f_inst)
            for alpha in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
                for s in range(20):
                    print(f'Inst {n + 1}/{len(instancies)}: {f_inst} | '
                          f'Seed: {s} | '
                          f'Initial Priority: Of | '
                          f'Alpha: {alpha}')
                    random.seed(s)
                    sol = cgrasp.construct(inst, alpha, 0, 'linehauls')
                    writer.writerow([f_inst, s, alpha, 'NoInitialNodes', sol['feasible'], sol['of']])
                    f.flush()
                    print(
                        f'Inst {n + 1}/{len(instancies)}: {f_inst} | '
                        f'Seed: {s} | '
                        f'Initial Priority: Distance | '
                        f'Alpha: {alpha}')
                    random.seed(s)
                    sol = cgrasp.construct_with_initial_nodes(inst, alpha, 0, 'linehauls', 'distance')
                    writer.writerow([f_inst, s, alpha, 'DistancePriority', sol['feasible'], sol['of']])
                    f.flush()
                    print(
                        f'Inst {n + 1}/{len(instancies)}: {f_inst} | '
                        f'Seed: {s} | '
                        f'Initial Priority: Demand | '
                        f'Alpha: {alpha}')
                    random.seed(s)
                    sol = cgrasp.construct_with_initial_nodes(inst, alpha, 0, 'linehauls', 'demand')
                    writer.writerow([f_inst, s, alpha, 'DemandPriority', sol['feasible'], sol['of']])
                    f.flush()

    print('Experiment finalitzat amb èxit')


def execute_test_feasibility_greedy_of_vs_greedy_demand():
    ruta_tv = Path('instances/TV')
    ruta_gj = Path('instances/GJ')
    instancies = list(ruta_tv.glob('*.csv')) + list(ruta_gj.glob('*.csv'))
    if not instancies:
        print("No s'ha trobat cap instància")
        return

    f_resultats = 'results/greedy_of_vs_greedy_demand.csv'
    existeix_fitxer = Path(f_resultats).exists()

    with open(f_resultats, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not existeix_fitxer:
            writer.writerow(['Inst', 'Greedy', 'Feasible', 'Of'])
        else:
            print('Ja existeix un fitxer amb els resultats')
            return

        for n in range(len(instancies)):
            f_inst = instancies[n]
            inst = instance.read_instance(f_inst)
            print(f'Inst {n+1}/{len(instancies)}: {f_inst}')
            sol = cgreedy.construct(inst, 1, 'linehauls')
            writer.writerow([f_inst, 'Demand', sol['feasible'], sol['of']])
            f.flush()
            print(f'Inst {n+1}/{len(instancies)}: {f_inst}')
            sol = cgreedy.construct(inst, 0, 'linehauls')
            writer.writerow([f_inst, 'Distance', sol['feasible'], sol['of']])
            f.flush()


if __name__ == '__main__':
    execute_test_grasp_alpha_constructive_sequential_w_and_wo_initial_nodes()