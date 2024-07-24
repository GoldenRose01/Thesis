from src.file_verifier import verify
from src.machine_learning import *
from Colorlib import *
import multiprocessing
import numpy as np
import argparse
import platform
import settings
import shutil
import sys
import time
import csv
import os
import logging


# Percorso al file .env per graphviz
env_path = '.env'
# Imposta la variabile d'ambiente PATH
os.environ['PATH'] = os.getenv('PATH')


def infoconsole():
    current_os = platform.system()

    if current_os == 'Windows':
        console_width = shutil.get_terminal_size().columns
    else:
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
            console_width = int(columns)
        except:
            console_width = shutil.get_terminal_size().columns

    return console_width


if __name__ == "__main__":

    if settings.selected_evaluation_edit_distance != "weighted_edit_distance":
        at_mainstart = f"{FUCSIA}Starting simulation with {settings.type_encoding} encoding & {settings.selected_evaluation_edit_distance}{RESET}"
    else:
        at_mainstart = f"{FUCSIA}Starting simulation with {settings.type_encoding} encoding & {settings.selected_evaluation_edit_distance} at {settings.wtrace_att},{settings.wactivities},{settings.wresource_att}{RESET}"

    print(at_mainstart.center(infoconsole()))

    # Verifica che i file di configurazione siano presenti
    verify.attributes_verifier("src/machine_learning/encoding/Settings")

    print_lock = multiprocessing.Lock()
    parser = argparse.ArgumentParser(
        description="Esperimenti per il monitoraggio dei processi prescrittivi basati sui risultati")
    parser.add_argument("-j", "--jobs", type=int,
                        help="Numero di lavori da eseguire in parallelo. Se -1 vengono utilizzate tutte le CPU disponibili.")
    args = parser.parse_args()

    jobs = None
    available_jobs = multiprocessing.cpu_count()
    if args.jobs:
        if args.jobs < -1 or args.jobs == 0:
            print("-j deve essere -1 o maggiore di 0")
            sys.exit(2)
        jobs = available_jobs if args.jobs == -1 else args.jobs

    final_results = {}
    start_time = time.time()
    # Inizia la simulazione
    if jobs is None or jobs == 1:
        for dataset in settings.datasets_names:
            _, res_obj, hyperparams, max_pref_length, min_pref_length, dt = rec_sys_exp(dataset)
            final_results[dataset] = res_obj
    else:
        tmp_list_results = []
        if platform.platform().split('-')[0] == 'macOS' or platform.platform().split('-')[0] == 'Darwin':
            with multiprocessing.get_context("spawn").Pool(processes=jobs) as pool:
                tmp_list_results = pool.map(rec_sys_exp, settings.datasets_names)
        else:
            pool = multiprocessing.Pool(processes=jobs)
            tmp_list_results = pool.map(rec_sys_exp, settings.datasets_names)
            pool.close()

        final_results = dict(tmp_list_results)

    # Definisci encoding e proportion
    encoding = f"{settings.type_encoding} with {settings.selected_evaluation_edit_distance}"
    if settings.selected_evaluation_edit_distance == "weighted_edit_distance":
        proportion = f"{settings.wtrace_att},{settings.wactivities},{settings.wresource_att}"
    else:
        proportion = "Null"

    # Salva i risultati finali in un file CSV
    with open(os.path.join(csv_dir), mode='a') as out_file:
        writer = csv.writer(out_file, delimiter=',')
        if not os.path.exists(csv_dir):
            writer.writerow([
                "Dataset",
                "Encoding",
                "Proportion",
                "Punteggio",
                "Migliore configurazione degli iperparametri",
                "Lunghezza minima del prefisso",
                "Lunghezza massima del prefisso",
                "Parametri dell'albero decisionale"
            ])
        for dataset in settings.datasets_names:
            writer.writerow([dataset] +
                            [round(100 * np.mean([getattr(res_obj, 'fscore') for res_obj in final_results[dataset]]),
                                   2)] +
                            [hyperparams] + [min_pref_length] + [max_pref_length] + [dt['parameters']])

    # Timer per simulazioni
    time_h_finale = (time.time() - start_time) / 3600
    time_m_finale = (time.time() - start_time) / 60

    print(CHOCOLATE + f"Le simulazioni hanno richiesto {time_h_finale:.2f} ore o {time_m_finale:.2f} minuti" + RESET)

    """
    verify.structurize_results("media/output/result")
    verify.remove_tmp_files("media/output")
    """

    if settings.enable_log:
        for filename in os.listdir():
            if filename.endswith('.log'):
                source_path = filename
                destination_path = os.path.join('log', filename)
                shutil.move(source_path, destination_path)
                print(f'Moved: {filename}')
