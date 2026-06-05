from pathlib import Path
from constructives import cgreedy
from algorithms import greedy
from structure import instance
import csv

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
            for estrategia in ['linehauls', 'both']:
                f_inst = instancies[n]
                print(f'Inst {n+1}/{len(instancies)}: {f_inst} | Construcció: {estrategia}')
                inst = instance.read_instance(f_inst)
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


if __name__ == '__main__':
    execute_test_greedy_initial_demand_priority()