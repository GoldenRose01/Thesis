from src.machine_learning import *
from src.machine_learning import recommender as rcm
from src.dataset_manager.datasetManager import *
import numpy as np
import settings
import time
import copy
import os
import platform
import argparse
import multiprocessing
import csv

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
    data,categoric_columns,numeric_columns = dataset_manager.read_dataset(os.path.join(os.getcwd(), settings.dataset_folder))

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

    (dt_input_trainval_encoded , prefix_length,
     ncu_data,indices,max_variations) = dt_input_trainval.encode_traces(numeric_columns, categoric_columns)

    # Lista dei risultati
    results = []

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
    tmp_paths, dt = rcm.train_path_recommender(data_log=data_log,
                                           train_val_log=train_val_log,
                                           val_log=val_log,
                                           train_log=train_log,
                                           labeling=labeling,
                                           support_threshold=settings.support_threshold_dict,
                                           dataset_name=dataset_name,
                                           output_dir=settings.output_dir,
                                           dt_input_trainval=dt_input_trainval_encoded)
    counter = 0

    # Scopre sul set di validazione con la migliore configurazione degli iperparametri di valutazione
    print(f"Hyperparametri per la valutazione per {dataset_name} ...")
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
            recommendations, evaluation = rcm.generate_recommendations_and_evaluation(test_log=val_log,
                                                                                  train_log=train_log,
                                                                                  labeling=labeling,
                                                                                  prefixing=prefixing,
                                                                                  rules=settings.rules,
                                                                                  paths=tmp_paths,
                                                                                  hyperparams_evaluation=hyperparams_evaluation,
                                                                                  eval_res=eval_res,
                                                                                  dt_input_trainval=dt_input_trainval,
                                                                                  dt_input_trainval_encoded=dt_input_trainval_encoded,
                                                                                  indices=indices,
                                                                                  max_variations=max_variations,
                                                                                  dataset_name=dataset_name
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
    print(f"MIGLIORE COMBINAZIONE DI IPERPARAMETRI {best_hyperparams_combination}")
    print(f"LUNGHEZZA MINIMA E MASSIMA DEI PREFISSI {min_prefix_length} {max_prefix_length_test}")

    # Test sul set di test con la migliore configurazione degli iperparametri di valutazione
    eval_res = None
    if settings.cumulative_res is True:
        eval_res = EvaluationResult()

    for pref_id, prefix_len in enumerate(prefix_lenght_list_test):
        print(
            f"<--- DATASET: {dataset_name}, LUNGHEZZA PREFISSO: {prefix_len}/{max_prefix_length_test} --->")
        prefixing = {
            "type": PrefixType.ONLY,
            "length": prefix_len
        }
        print("valutazione", prefix_len, "/", max_prefix_length_test)
        recommendations, evaluation = rcm.generate_recommendations_and_evaluation(test_log=test_log,
                                                                              train_log=train_log,
                                                                              labeling=labeling,
                                                                              prefixing=prefixing,
                                                                              rules=settings.rules,
                                                                              paths=paths,
                                                                              hyperparams_evaluation=best_hyperparams_combination,
                                                                              eval_res=eval_res,
                                                                              indices=indices,
                                                                              max_variations=max_variations,
                                                                              dt_input_trainval=dt_input_trainval,
                                                                              dt_input_trainval_encoded=dt_input_trainval_encoded,
                                                                              dataset_name=dataset_name
                                                                              )
        results.append(evaluation)
        if settings.cumulative_res is True:
            eval_res = copy.deepcopy(evaluation)

        for metric in ["fscore"]:  # ["accuracy", "fscore", "auc", "gain"]:
            value = getattr(results[pref_id], metric)
            print(f"{metric}:{value}".format(metric=metric, value=value))
    plot = PlotResult(results, prefix_lenght_list_test, settings.results_dir)

    for metric in ["fscore"]:
        plot.toPng(metric, f"{dataset_name}_{settings.type_encoding}_{settings.selected_evaluation_edit_distance}_{metric}")

    # Salva i risultati della valutazione dei prefissi in un file CSV
    rcm.prefix_evaluation_to_csv(results, dataset_name)
    return dataset_name, results, best_hyperparams_combination, max_prefix_length_test, min_prefix_length, dt