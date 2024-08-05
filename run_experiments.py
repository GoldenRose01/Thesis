from src.machine_learning import recommender as rcm
from src.dataset_manager.datasetManager import *
import src.file_verifier.Postprocessing as postprocessing
import src.file_verifier.verify as verify
from src.machine_learning import *
from Colorlib.Colors import *
import numpy as np
import settings
import logging
import shutil
import time
import copy
import os
import sys


class LoggerWriter:
    def __init__(self, level):
        self.level = level
        self.buffer = ''

    def write(self, message):
        if message != '\n':
            self.buffer += message
        if '\n' in message:
            self.level(self.buffer)
            self.buffer = ''

    def flush(self):
        self.level(self.buffer)
        self.buffer = ''


def generate_log_filename(dataset_name):
    if settings.selected_evaluation_edit_distance == "weighted_edit_distance":
        filename = (f"{dataset_name}_{settings.ruleprefix}{settings.type_encoding} encoding e"
                    f" {settings.selected_evaluation_edit_distance} at ({settings.wtrace_att}%,"
                    f"{settings.wactivities}%,{settings.wresource_att}%).log")
    else:
        filename = (f"{dataset_name}_{settings.ruleprefix}{settings.type_encoding} encoding e "
                    f"{settings.selected_evaluation_edit_distance}.log")
    return filename


# Funzione principale che esegue l'esperimento di sistema di raccomandazione
def rec_sys_exp(dataset_name):

    if settings.enable_log:
        # Generazione del nome del file di log
        log_filename = generate_log_filename(dataset_name)

        # Impostazione del logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Creazione di un handler che scrive su file con il nome dinamico
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # Creazione di un handler per il console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Creazione di un formatter e aggiunta agli handler
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Aggiunta degli handler al logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Ridirezione di stdout e stderr verso il logger
        sys.stdout = LoggerWriter(logger.info)

    # Simulation Timer start
    start_time_exp = time.time()
    at_startexp = f"Starting the simulation on {dataset_name}"
    print(f"{BLUE}{at_startexp.center(main.infoconsole())}{RESET}")


    # ================ inputs ================

    # Ricrea la cartella di output
    # shutil.rmtree("media/output", ignore_errors=True)
    # os.makedirs(os.path.join(results_dir))

    # Genera delle regole (commentate in questo codice)
    # settings.rules["activation"] = generate_rules(settings.rules["activation"])
    # settings.rules["correlation"] = generate_rules(settings.rules["correlation"])

    # Crea un oggetto DatasetManager per il dataset specificato
    dataset_manager = DatasetManager(dataset_name.lower())
    data, categoric_columns, numeric_columns = dataset_manager.read_dataset(
        os.path.join(os.getcwd(), settings.dataset_folder))

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
        "target": TraceLabel.TRUE,
        "trace_lbl_attr": dataset_manager.label_col,
        "trace_label": 'regular',
        "custom_threshold": 0.0
    }

    """
    labeling = {
        "type": LabelType.TRACE_CATEGORICAL_ATTRIBUTES,
        "threshold_type": "",
        "target": TraceLabel.TRUE,  # lower than a threshold considered as True
        "trace_lbl_attr": dataset_manager.label_col,
        "trace_label": dataset_manager.pos_label,
        "custom_threshold": 0.0
    }
    """

    """
    labeling = {
        "type": LabelType.TRACE_DURATION,
        "threshold_type": LabelThresholdType.LABEL_MEAN,
        "target": TraceLabel.TRUE,
        "trace_attribute": "",
        "custom_threshold": 0.0
        }
    """
    # Percorsi dei file da cui leggere gli attributi
    trace_attributes_path = 'src/machine_learning/encoding/Settings/Trace_att.txt'
    resource_attributes_path = 'src/machine_learning/encoding/Settings/Resource_att.txt'
    trace_attributes = read_attributes_from_file(trace_attributes_path, dataset_name)
    resource_attributes = read_attributes_from_file(resource_attributes_path, dataset_name)

    # Creazione dell'oggetto Encoding
    dt_input_trainval = Encoding(train_val_log, resource_attributes, trace_attributes)

    (dt_input_trainval_encoded,
     prefix_length,
     ncu_data,
     indices,
     max_variations,
     features) = dt_input_trainval.encode_traces(numeric_columns, categoric_columns)

    verify.printprefixlength(dataset_name, prefix_length)
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

    # Lista delle combinazioni di iperparametri per l' evaluation
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
                                               dt_input_trainval=dt_input_trainval_encoded,
                                               resource_attributes=resource_attributes,
                                               trace_attributes=trace_attributes,
                                               )
    counter = 0

    # Scopre sul set di validazione con la migliore configurazione degli iperparametri di valutazione
    if settings.Allprint:
        at_hypval = f"Hyperparametri per la valutazione per {dataset_name}"
        print(f"{LILAC}{at_hypval.center(main.infoconsole())}{RESET}")

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
            if settings.Allprint:
                at_counter = f"Counter:{counter}"
                at_rec = f"raccomandazione{prefix_len}/{max_prefix_length_val}"
                print(f"{AMETHYST_PURPLE}{at_counter.center(main.infoconsole())}{RESET}")
                print(f"{LAVENDER_GRAY}{at_rec.center(main.infoconsole())}{RESET}")
            (recommendations,
             evaluation) = rcm.generate_recommendations_and_evaluation(
                                    test_log=val_log,
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
                                    dataset_name=dataset_name,
                                    prefix_max=prefix_length,
                                    features=features,
                                    resource_attributes=resource_attributes,
                                    trace_attributes=trace_attributes,
                                    )
            if settings.cumulative_res is True:
                eval_res = copy.deepcopy(evaluation)
            res_val_list.append(evaluation.fscore)
        results_hyperparams_evaluation[hyperparams_evaluation] = np.mean(res_val_list)
        time_f = (time.time() - time_i) / 60.
        time_h = (time.time() - time_i) / 3600
        at_simulation = f"Simulation: {counter} Time: {time_f:.2f} minuti o {time_h:.2f} ore\n"
        print(f"{ORANGE}{at_simulation.center(main.infoconsole())}{RESET}")

    results_hyperparams_evaluation = dict(sorted(results_hyperparams_evaluation.items(), key=lambda item: item[1]))
    best_hyperparams_combination = list(results_hyperparams_evaluation.keys())[-1]
    paths = tmp_paths
    at_hypcombo = f"Best hyperparams combo {best_hyperparams_combination}"
    print(f"{PINK}{at_hypcombo.center(main.infoconsole())}{RESET}")

    at_maxmin = (f"{MUSTARD}MIN ({SALMON}{min_prefix_length}{MUSTARD})"
                 f" & MAX ({SALMON}{max_prefix_length_test}{MUSTARD}) Prefix Length {RESET}")
    print(f"{at_maxmin.center(main.infoconsole())}\n")

    # Test sul set di test con la migliore configurazione degli iperparametri di valutazione
    eval_res = None
    if settings.cumulative_res is True:
        eval_res = EvaluationResult()

    for pref_id, prefix_len in enumerate(prefix_lenght_list_test):
        at_prefix = f"<--- DATASET: {dataset_name}, Lenght of the prefix: {prefix_len}/{max_prefix_length_test} --->\n"
        print(f"{GRAY_DARK}{at_prefix.center(main.infoconsole())}{RESET}")

        prefixing = {
            "type": PrefixType.ONLY,
            "length": prefix_len
        }
        at_eval = f"Evaluation{prefix_len}/{max_prefix_length_test}"

        print(f"{GRAY_LIGHT}{at_eval.center(main.infoconsole())}{RESET}\n")

        (recommendations,
         evaluation) = rcm.generate_recommendations_and_evaluation(
                                test_log=test_log,
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
                                dataset_name=dataset_name,
                                prefix_max=prefix_length,
                                features=features,
                                resource_attributes=resource_attributes,
                                trace_attributes=trace_attributes,
                                )
        results.append(evaluation)
        if settings.cumulative_res is True:
            eval_res = copy.deepcopy(evaluation)

        for metric in ["fscore"]:  # ["accuracy", "fscore", "auc", "gain"]:
            value = getattr(results[pref_id], metric)
            if settings.Allprint is True:
                print(f"{metric}:{value}".format(metric=metric, value=value))

    plot = PlotResult(results, prefix_lenght_list_test, settings.results_dir)

    for metric in ["fscore"]:
        if settings.selected_evaluation_edit_distance != "weighted_edit_distance":
            plot.toPng(metric,
                       f"{dataset_name}_{settings.ruleprefix}{settings.type_encoding}_"
                       f"{settings.selected_evaluation_edit_distance}_{metric}")
        else:
            plot.toPng(metric,
                       f"{dataset_name}_{settings.ruleprefix}{settings.type_encoding}_"
                       f"{settings.selected_evaluation_edit_distance}{settings.wtrace_att}%,"
                       f"{settings.wactivities}%,{settings.wresource_att}%_{metric}")
    # Salva i risultati della valutazione dei prefissi in un file CSV
    namefile = rcm.prefix_evaluation_to_csv(results, dataset_name)

    # Timer per simulazioni
    time_h_exp = (time.time() - start_time_exp) / 3600
    time_m_exp = (time.time() - start_time_exp) / 60

    if settings.selected_evaluation_edit_distance != "weighted_edit_distance":
        dataset_info = {
            'dataset_name': dataset_name,
            'ruleprefix': settings.ruleprefix,
            'type_encoding': settings.type_encoding,
            'selected_evaluation_edit_distance': settings.selected_evaluation_edit_distance,
            'namefile':namefile
        }
    else:
        dataset_info = {
            'dataset_name': dataset_name,
            'rule_prefix': settings.ruleprefix,
            'type_encoding': settings.type_encoding,
            'selected_evaluation_edit_distance': 'weighted_edit_distance',
            'wtrace_att': settings.wtrace_att,
            'wactivities': settings.wactivities,
            'wresource_att': settings.wresource_att,
            'namefile': namefile,
        }

    if not os.path.exists(settings.postprocessing_folder):
        os.makedirs(settings.postprocessing_folder)



    verify.timeprinter(dataset_name, settings.type_encoding, settings.selected_evaluation_edit_distance,
                       settings.wtrace_att, settings.wactivities, settings.wresource_att, time_m_exp)

    postprocessing.process_and_update_summary(settings.results_dir, settings.postprocessing_folder, dataset_info)

    at_endexp = f"{dataset_name} simulation required {time_h_exp:.2f}H or {time_m_exp:.2f}min"
    print(f"\n{GREEN}{at_endexp.center(main.infoconsole())}{RESET}\n\n")

    symbol = "="
    print(f"{IVORY}{symbol * main.infoconsole()}{RESET}\n\n")

    return dataset_name, results, best_hyperparams_combination, max_prefix_length_test, min_prefix_length, dt
