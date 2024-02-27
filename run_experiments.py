from src.dataset_manager.datasetManager import DatasetManager
from src.machine_learning import *
from pm4py.objects.conversion.log import converter as log_converter
import argparse
import multiprocessing
import sys
import time
import numpy as np
import csv
import copy
import os
import subprocess
import platform
import settings

# Percorso al file .env per graphviz
env_path = '.env'
# Imposta la variabile d'ambiente PATH
os.environ['PATH'] = os.getenv('PATH')


# ___Verifica se i file Resource_att.txt e Trace_att.txt esistono nella cartella desiderata___#
def attributes_verifier(directory):
    resource_filename = "Resource_att.txt"
    trace_filename = "Trace_att.txt"
    resource_att_path = directory + "/" + resource_filename
    trace_att_path = directory + "/" + trace_filename
    if not os.path.exists(resource_att_path) or not os.path.exists(trace_att_path):
        print("File non trovati. Esecuzione degli script Xesreader.py e csvreader.")
        # Esegui csvreader.py e poi converti xes to csv
        subprocess.run(["python", "Mediamanager/csvreader.py"])
        subprocess.run(["python", "Mediamanager/xestocsv.py"])
    else:
        print("File trovati,inizio esperimento")


def remove_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            os.remove(os.path.join(directory, filename))
    print("File eliminati")


def rename_and_convert_to_log(df, dataset_manager):
    renamed_df = df.rename(
        columns={
            dataset_manager.timestamp_col: 'time:timestamp',
            dataset_manager.case_id_col: 'case:concept:name',
            dataset_manager.activity_col: 'concept:name'
        }
    )
    return log_converter.apply(renamed_df)

def filtercatdf(dt_input_trainval_encoded, categoric_columns):
    df_encoded = dt_input_trainval_encoded
    existing_categoric_cols = [col for col in df_encoded.features if any(feature in col for feature in categoric_columns+['prefix'])]
    df_encoded_data_cat_num_col = pd.DataFrame(df_encoded.encoded_data, columns=df_encoded.features)
    df_categorici = df_encoded_data_cat_num_col[existing_categoric_cols]
    dati_categorici_as_lists = df_categorici.values.tolist()

    return dati_categorici_as_lists
def filternumdf(dt_input_trainval_encoded, numeric_columns):
    df_encoded = dt_input_trainval_encoded
    existing_numeric_cols = [col for col in df_encoded.features if any(feature in col for feature in numeric_columns)]
    df_encoded_data_cat_num_col = pd.DataFrame(df_encoded.encoded_data, columns=df_encoded.features)
    df_numerici = df_encoded_data_cat_num_col[existing_numeric_cols]
    dati_numerici_as_lists = df_numerici.values.tolist()

    return dati_numerici_as_lists



# Funzione principale che esegue l'esperimento di sistema di raccomandazione
def rec_sys_exp(dataset_name):
    # ================ inputs ================

    # Ricrea la cartella di output
    # shutil.rmtree("media/output", ignore_errors=True)
    # os.makedirs(os.path.join(results_dir))

    # Genera delle regole (commentate in questo codice)
    # settings.rules["activation"] = generate_rules(settings.rules["activation"])
    # settings.rules["correlation"] = generate_rules(settings.rules["correlation"])

    # Crea un oggetto DatasetManager per il dataset specificato
    dataset_manager = DatasetManager(dataset_name.lower())
    data = dataset_manager.read_dataset(os.path.join(os.getcwd(), settings.dataset_folder))

    # Ottieni le colonne categoriche e numeriche dal DatasetManager
    categoric_columns = dataset_manager.dynamic_cat_cols + dataset_manager.static_cat_cols
    numeric_columns = dataset_manager.dynamic_num_cols + dataset_manager.static_num_cols

    # Suddivide il dataset in training e test
    train_val_ratio = 0.8
    if dataset_name == "bpic2015_4_f2":
        train_val_ratio = 0.85
    train_ratio = 0.9
    train_val_df, test_df = dataset_manager.split_data_strict(data, train_val_ratio)
    train_df, val_df = dataset_manager.split_data(train_val_df, train_ratio, split="random")

    # Determina le lunghezze minime e massime dei prefissi (troncate)
    min_prefix_length = 1
    if "traffic_fines" in dataset_name:
        max_prefix_length_test, max_prefix_length_val = 9, 9
    elif "bpic2017" in dataset_name:
        max_prefix_length_test = min(20, dataset_manager.get_pos_case_length_quantile(test_df, 0.90))
        max_prefix_length_val = min(20, dataset_manager.get_pos_case_length_quantile(val_df, 0.90))
    else:
        max_prefix_length_test = min(40, dataset_manager.get_pos_case_length_quantile(test_df, 0.90))
        max_prefix_length_val = min(40, dataset_manager.get_pos_case_length_quantile(val_df, 0.90))

    # Rinomina le colonne del dataset
    data = data.rename(
        columns={dataset_manager.timestamp_col: 'time:timestamp',
                dataset_manager.case_id_col: 'case:concept:name',
                dataset_manager.activity_col: 'concept:name'
                })

    train_df = train_df.rename(
        columns={dataset_manager.timestamp_col: 'time:timestamp',
                 dataset_manager.case_id_col: 'case:concept:name',
                 dataset_manager.activity_col: 'concept:name'
                 })
    test_df = test_df.rename(
        columns={dataset_manager.timestamp_col: 'time:timestamp',
                 dataset_manager.case_id_col: 'case:concept:name',
                 dataset_manager.activity_col: 'concept:name'
                 })
    val_df = val_df.rename(
        columns={dataset_manager.timestamp_col: 'time:timestamp',
                 dataset_manager.case_id_col: 'case:concept:name',
                 dataset_manager.activity_col: 'concept:name'
                 })
    train_val_df = train_val_df.rename(
        columns={dataset_manager.timestamp_col: 'time:timestamp',
                 dataset_manager.case_id_col: 'case:concept:name',
                 dataset_manager.activity_col: 'concept:name'
                 })

    # Converte i dataframe in oggetti di log PM4Py
    val_log = log_converter.apply(val_df)
    train_log = log_converter.apply(train_df)
    test_log = log_converter.apply(test_df)
    train_val_log = log_converter.apply(train_val_df)
    data_log = log_converter.apply(data)

    # Definizione delle etichette
    labeling = {
        "type": LabelType.TRACE_CATEGORICAL_ATTRIBUTES,
        "threshold_type": "",
        "target": TraceLabel.TRUE,  # inferiore a una soglia considerata come True
        "trace_lbl_attr": dataset_manager.label_col,
        "trace_label": dataset_manager.pos_label,
        "custom_threshold": 0.0
    }

    # Creazione dell'oggetto Encoding
    dt_input_trainval = Encoding(train_val_log)
    dt_input_trainval_encoded , prefix_length = dt_input_trainval.encode_traces()

    # Lista dei risultati
    results = []

    # Creazione dell'oggetto Numeric Encoding e Categorical Encoding
    numericaldf = filternumdf(dt_input_trainval_encoded,numeric_columns)
    categoricaldf = filtercatdf(dt_input_trainval_encoded, categoric_columns)

    # Imposta la lunghezza massima dei prefissi di test e validazione
    if max_prefix_length_test > prefix_length:
        max_prefix_length_test = prefix_length - 1
    if max_prefix_length_val > prefix_length:
        max_prefix_length_val = prefix_length - 1

    # Lista delle lunghezze dei prefissi per il test e la validazione
    prefix_lenght_list_test = list(range(min_prefix_length, max_prefix_length_test + 1))
    prefix_lenght_list_val = list(range(min_prefix_length, max_prefix_length_val + 1))

    # Lista delle combinazioni di iperparametri per l'evalutazione
    hyperparams_evaluation_list = []
    results_hyperparams_evaluation = {}
    hyperparams_evaluation_list_baseline = []

    for v1 in settings.sat_threshold_list:
        # La baseline sceglie il percorso con la probabilità più alta
        hyperparams_evaluation_list_baseline.append((v1,) + (0, 0, 1))
        for v2 in settings.weight_combination_list:
            hyperparams_evaluation_list.append((v1,) + v2)

    # Esegue la creazione dei percorsi di allenamento
    tmp_paths, dt = train_path_recommender(data_log=data_log,
                                           train_val_log=train_val_log,
                                           val_log=val_log,
                                           train_log=train_log,
                                           labeling=labeling,
                                           support_threshold=settings.support_threshold_dict,
                                           dataset_name=dataset_name,
                                           output_dir=settings.output_dir,
                                           dt_input_trainval=dt_input_trainval_encoded)
    counter = 0

    num_tmp_paths,num_dt=train_path_recommender(data_log=data_log,
                                                train_val_log=train_val_log,
                                                val_log=val_log,
                                                train_log=train_log,
                                                labeling=labeling,
                                                support_threshold=settings.support_threshold_dict,
                                                dataset_name=dataset_name,
                                                output_dir=settings.output_dir,
                                            dt_input_trainval=numericaldf)


    cat_tmp_paths,cat_dt=train_path_recommender(data_log=data_log,
                                           train_val_log=train_val_log,
                                           val_log=val_log,
                                           train_log=train_log,
                                           labeling=labeling,
                                           support_threshold=settings.support_threshold_dict,
                                           dataset_name=dataset_name,
                                           output_dir=settings.output_dir,
                                           dt_input_trainval=categoricaldf)

    # Scopre sul set di validazione con la migliore configurazione degli iperparametri di valutazione
    print("Hyperparametri per la valutazione per {dataset_name} ...")
    if settings.compute_baseline:
        hyperparams_evaluation_list = hyperparams_evaluation_list_baseline

    for hyperparams_evaluation in hyperparams_evaluation_list:
        counter = counter + 1
        time_i = time.time()
        res_val_list = []
        eval_res = None
        if settings.cumulative_res is True:
            eval_res = EvaluationResult()
        for pref_id, prefix_len in enumerate(prefix_lenght_list_val):
            prefixing = {
                "type": PrefixType.ONLY,
                "length": prefix_len
            }
            print("Counter: ", counter)
            print("raccomandazione", prefix_len, "/", max_prefix_length_val)
            recommendations, evaluation = generate_recommendations_and_evaluation(test_log=val_log,
                                                                                  train_log=train_log,
                                                                                  labeling=labeling,
                                                                                  prefixing=prefixing,
                                                                                  rules=settings.rules,
                                                                                  paths=tmp_paths,
                                                                                  hyperparams_evaluation=hyperparams_evaluation,
                                                                                  eval_res=eval_res,
                                                                                  dt_input_trainval=dt_input_trainval
                                                                                  )
            numeric_recommendations, numeric_evaluation = generate_recommendations_and_evaluation(test_log=val_log,
                                                                                  train_log=train_log,
                                                                                  labeling=labeling,
                                                                                  prefixing=prefixing,
                                                                                  rules=settings.rules,
                                                                                  paths=num_tmp_paths,
                                                                                  hyperparams_evaluation=hyperparams_evaluation,
                                                                                  eval_res=eval_res,
                                                                                  dt_input_trainval=num_dt
                                                                                  )
            categorical_recommendations, categorical_evaluation = generate_recommendations_and_evaluation(test_log=val_log,
                                                                                  train_log=train_log,
                                                                                  labeling=labeling,
                                                                                  prefixing=prefixing,
                                                                                  rules=settings.rules,
                                                                                  paths=cat_tmp_paths,
                                                                                  hyperparams_evaluation=hyperparams_evaluation,
                                                                                  eval_res=eval_res,
                                                                                  dt_input_trainval=cat_dt
                                                                                  )
            if settings.cumulative_res is True:
                eval_res = copy.deepcopy(evaluation)
            res_val_list.append(evaluation.fscore)
        results_hyperparams_evaluation[hyperparams_evaluation] = np.mean(res_val_list)
        time_f = (time.time() - time_i) / 60.
        time_h = (time.time() - time_i) / 3600
        print("Simulazione: ", counter, ", tempo: ", time_f, "minuti o ", time_h, "ore")

    results_hyperparams_evaluation = dict(sorted(results_hyperparams_evaluation.items(), key=lambda item: item[1]))
    best_hyperparams_combination = list(results_hyperparams_evaluation.keys())[-1]
    paths = tmp_paths
    best_hyperparams_combination = best_hyperparams_combination
    print("MIGLIORE COMBINAZIONE DI IPERPARAMETRI {best_hyperparams_combination}")
    print("LUNGHEZZA MINIMA E MASSIMA DEI PREFISSI {min_prefix_length} {max_prefix_length_test}")

    # Test sul set di test con la migliore configurazione degli iperparametri di valutazione
    eval_res = None
    if settings.cumulative_res is True:
        eval_res = EvaluationResult()

    for pref_id, prefix_len in enumerate(prefix_lenght_list_test):
        print(
            "<--- DATASET: {dataset_name}, LUNGHEZZA PREFISSO: {prefix_len}/{max_prefix_length_test} --->")
        prefixing = {
            "type": PrefixType.ONLY,
            "length": prefix_len
        }
        print("valutazione", prefix_len, "/", max_prefix_length_test)
        recommendations, evaluation = generate_recommendations_and_evaluation(test_log=test_log,
                                                                              train_log=train_log,
                                                                              labeling=labeling,
                                                                              prefixing=prefixing,
                                                                              rules=settings.rules,
                                                                              paths=paths,
                                                                              hyperparams_evaluation=best_hyperparams_combination,
                                                                              eval_res=eval_res,
                                                                              dt_input_trainval=dt_input_trainval
                                                                              )
        numeric_recommendations, numeric_evaluation = generate_recommendations_and_evaluation(test_log=test_log,
                                                                              train_log=train_log,
                                                                              labeling=labeling,
                                                                              prefixing=prefixing,
                                                                              rules=settings.rules,
                                                                              paths=num_tmp_paths,
                                                                              hyperparams_evaluation=best_hyperparams_combination,
                                                                              eval_res=eval_res,
                                                                              dt_input_trainval=dati_numerici_as_lists
                                                                              )
        categorical_recommendations, categorical_evaluation = generate_recommendations_and_evaluation(test_log=test_log,
                                                                              train_log=train_log,
                                                                              labeling=labeling,
                                                                              prefixing=prefixing,
                                                                              rules=settings.rules,
                                                                              paths=cat_tmp_paths,
                                                                              hyperparams_evaluation=best_hyperparams_combination,
                                                                              eval_res=eval_res,
                                                                              dt_input_trainval=dati_categorici_as_lists
                                                                              )
        results.append(evaluation)
        if settings.cumulative_res is True:
            eval_res = copy.deepcopy(evaluation)

        for metric in ["fscore"]:  # ["accuracy", "fscore", "auc", "gain"]:
            print("{metric}: {value}".format(metric=metric, value=getattr(results[pref_id], metric)))
    plot = PlotResult(results, prefix_lenght_list_test, settings.results_dir)

    for metric in ["fscore"]:
        plot.toPng(metric, "{dataset_name}_{metric}")

    # Salva i risultati della valutazione dei prefissi in un file CSV
    recommender.prefix_evaluation_to_csv(results, dataset_name)
    return dataset_name, results, best_hyperparams_combination, max_prefix_length_test, min_prefix_length, dt


if __name__ == "__main__":
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

    # Elimina i file txt presenti in src/machine_learning/encoding
    # remove_files("src/machine_learning/encoding/Settings")
    # remove_files("media/input/csvconverted")
