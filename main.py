from src.machine_learning import *
import argparse
import multiprocessing
import sys
import time
import numpy as np
import csv
import os
import platform
import settings

# Percorso al file .env per graphviz
env_path = '.env'
# Imposta la variabile d'ambiente PATH
os.environ['PATH'] = os.getenv('PATH')

if __name__ == "__main__":

    # Verifica che i file di configurazione siano presenti
    attributes_verifier("src/machine_learning/encoding/Settings")

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
    #Inizia la simulazione
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

    # Salva i risultati finali in un file CSV
    with open(os.path.join(settings.output_dir, "results.csv"), mode='a') as out_file:
        writer = csv.writer(out_file, delimiter=',')
        writer.writerow(
            ["Dataset", "Punteggio", "Migliore configurazione degli iperparametri", "Lunghezza minima del prefisso",
             "Lunghezza massima del prefisso", "Parametri dell'albero decisionale"])
        for dataset in settings.datasets_names:
            writer.writerow([dataset] +
                            [round(100 * np.mean([getattr(res_obj, 'fscore') for res_obj in final_results[dataset]]),
                                   2)] +
                            [hyperparams] + [min_pref_length] + [max_pref_length] + [dt['parameters']])
    time_h_finale = (time.time() - start_time) / 3600
    time_m_finale = (time.time() - start_time) / 60

    print("Le simulazioni hanno richiesto " + str(time_h_finale) + " ore o " + str(time_m_finale) + " minuti")

    # Elimina file configurazione trace_id e resource_attribute
    if input("Vuoi eliminare i preset di trace_id e resource_attribute? (y/n/Y/N): ") == "y"|"Y":
        remove_files("src/machine_learning/encoding/Settings")
        remove_files("media/input/csvconverted")
    else:
        print("I file non sono stati eliminati")