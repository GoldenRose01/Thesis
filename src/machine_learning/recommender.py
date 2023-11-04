import copy  # Importa la libreria copy per la copia profonda degli oggetti.
# Importa altri moduli e librerie necessari che sembrano non essere presenti nel codice fornito.
#from src.machine_learning.utils import *
#from src.machine_learning.apriori import *
#from src.machine_learning.encoding import *
from src.machine_learning.decision_tree import *  # Importa il modulo decision_tree dalla directory src.machine_learning.
from src.models import EvaluationResult  # Importa la classe EvaluationResult dalla directory src.models.
from src.constants import *  # Importa tutte le costanti definite nella directory src.constants.
from src.machine_learning import evaluateEditDistance  # Importa la funzione evaluateEditDistance dalla directory src.machine_learning.
import csv  # Importa il modulo csv per la manipolazione dei file CSV.
import numpy as np  # Importa la libreria numpy per operazioni matematiche su array.
import settings  # Importa il modulo settings, che sembra essere un file di configurazione personalizzato.
from sklearn import metrics  # Importa il modulo metrics dalla libreria sklearn per valutare i modelli.

# Crea una classe ParamsOptimizer per ottimizzare i parametri del modello.
class ParamsOptimizer:
    def __init__(self, data_log, train_val_log, val_log, train_log, parameters, labeling, checkers, rules, min_prefix_length, max_prefix_length):
        # Inizializza la classe con i parametri necessari.
        self.parameter_names = parameters.keys()  # Ottiene i nomi dei parametri.
        self.val_log = val_log  # Registro di validazione.
        self.data_log = data_log  # Registro dati.
        self.train_val_log = train_val_log  # Registro di allenamento e validazione.
        self.param_grid = [element for element in itertools.product(*parameters.values())]  # Crea una griglia dei parametri possibili.
        self.train_log = train_log  # Registro di allenamento.
        self.parameters = parameters  # Parametri del modello.
        self.labeling = labeling  # Etichettatura dei dati.
        self.checkers = checkers  # Controllori.
        self.rules = rules  # Regole.
        self.model_grid = []  # Griglia dei modelli.
        self.min_prefix_length = min_prefix_length  # Lunghezza minima del prefisso.
        self.max_prefix_length = max_prefix_length  # Lunghezza massima del prefisso.

    # Funzione per la ricerca nella griglia dei parametri.
    def params_grid_search(self, dataset_name, constr_family):
        categories = [TraceLabel.FALSE.value, TraceLabel.TRUE.value]  # Definisci categorie.

        for param_id, param_tuple in enumerate(self.param_grid):
            model_dict = {'dataset_name': dataset_name, 'constr_family': constr_family, 'parameters': param_tuple,
                          'f1_score_val': None, 'f1_score_train': None, 'f1_prefix_val': None, 'max_depth': 0,
                          'id': param_id, 'model': None, 'frequent_events': None, 'frequent_pairs': None}

            (frequent_events_train, frequent_pairs_train) = generate_frequent_events_and_pairs(self.data_log,
                                                                                               param_tuple[0])

            # Genera input per l'albero decisionale
            dt_input_train = Encoding(self.train_log, labeling=self.labeling)
            dt_input_train.encode_traces
            dt_input_val = Encoding(self.val_log, labeling=self.labeling)
            dt_input_val.encode_traces

            X_train = pd.DataFrame(dt_input_train.encoded_data, columns=dt_input_train.features)
            y_train = pd.Categorical(dt_input_train.labels, categories=categories)

            X_val = pd.DataFrame(dt_input_val.encoded_data, columns=dt_input_val.features)
            y_val = pd.Categorical(dt_input_val.labels, categories=categories)

            # Genera l'albero decisionale e il punteggio sul set di validazione
            dtc, f1_score_val, f1_score_train = generate_decision_tree(X_train, X_val, y_train, y_val, class_weight=param_tuple[1], min_samples_split=param_tuple[2])
            paths = generate_paths(dtc=dtc, dt_input_features=dt_input_train.features, target_label=self.labeling["target"])

            # Valutazione sui prefissi del set di validazione
            results = []
            for pref_id, prefix_len in enumerate(range(self.min_prefix_length, self.max_prefix_length + 1)):
                prefixing = {
                    "type": PrefixType.ONLY,
                    "length": prefix_len
                }

                evaluation = evaluate_recommendations(input_log=self.val_log,
                                                      labeling=self.labeling, prefixing=prefixing,
                                                      rules=self.rules, paths=paths)
                results.append(evaluation)

            model_dict['model'] = dtc
            model_dict['f1_score_val'] = f1_score_val
            model_dict['f1_score_train'] = f1_score_train
            model_dict['f1_prefix_val'] = np.average([res.fscore for res in results])
            model_dict['frequent_events'] = frequent_events_train
            model_dict['frequent_pairs'] = frequent_pairs_train
            self.model_grid.append(model_dict)

        # Retraining dell'albero decisionale utilizzando il set di allenamento e validazione con i migliori parametri testati sul set di validazione
        sorted_models = sorted(self.model_grid, key=lambda d: d['f1_prefix_val'])
        best_model_dict = sorted_models[-1]

        # Input per l'albero decisionale con il set di allenamento e validazione
        dt_input_trainval = Encoding(self.train_val_log, labeling=self.labeling)
        dt_input_trainval.encode_traces
        dt_input_val = Encoding(self.val_log, labeling=self.labeling)
        dt_input_val.encode_traces

        X_train_val = pd.DataFrame(dt_input_trainval.encoded_data, columns=dt_input_trainval.features)
        y_train_val = pd.Categorical(dt_input_trainval.labels, categories=categories)
        X_val = pd.DataFrame(dt_input_val.encoded_data, columns=dt_input_val.features)
        y_val = pd.Categorical(dt_input_val.labels, categories=categories)

        dtc, _, _ = generate_decision_tree(X_train_val, X_val, y_train_val, y_val,
                                           class_weight=best_model_dict['parameters'][1],
                                           min_samples_split=best_model_dict['parameters'][2])
        best_model_dict['model'] = dtc
        best_model_dict['max_depth'] = dtc.tree_.max_depth

        del best_model_dict["frequent_events"]
        del best_model_dict["frequent_pairs"]
        return best_model_dict, dt_input_trainval.features

# Definisci una funzione per generare raccomandazioni basate su un prefisso e un percorso
def recommend(prefix, path, dt_input_trainval):
    recommendation = ""

    prefixes = []
    for trace in prefix:
        prefixes.append(trace['concept:name'])
    num_prefixes = len(prefixes)

    for rule in path.rules:
        feature, state, parent = rule

        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2

        if (num1) > num_prefixes:
            rec = np.zeros(num1, dtype=int)
            rec[num1 - 1] = int(num2)
            rec = rec.tolist()

            rec_str = dt_input_trainval.decode(rec)
            for column in rec_str.columns:
                if (rec_str[column].iloc[0] != '0') and rec_str[column].notnull().any():
                    if state == TraceState.VIOLATED:
                        recommendation += "" + column + " should not be " + rec_str[column].iloc[0] + "; "
                    if state == TraceState.SATISFIED:
                        recommendation += "" + column + " should be " + rec_str[column].iloc[0] + "; "

    return recommendation

# Definisci una funzione per valutare la conformità di un trace rispetto a un percorso
def evaluate(trace, path, num_prefixes, dt_input_trainval, sat_threshold, labeling):
    is_compliant = True
    activities = []

    for idx, event in enumerate(trace):
        for attribute_key, attribute_value in event.items():
            if (attribute_key == 'concept:name'):
                activities.append(attribute_value)

    activities = dt_input_trainval.encode(activities)

    hyp = []
    hypInt = []
    for column in activities.columns:
        hyp.extend(activities[column].values)
    hyp = np.array(hyp)
    hyp = hyp.tolist()

    for value in hyp:
        if isinstance(value, str) and value.isdigit():
            hypInt.append(int(value))
    if len(hypInt) > 0:
        hyp = copy.deepcopy(hypInt)
    hyp = hyp[num_prefixes:]

    n_max = 0

    for rule in path.rules:
        feature, state, parent = rule
        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2
        if (num1) > n_max:
            n_max = num1

    ref = np.zeros(n_max, dtype=int)

    for rule in path.rules:
        feature, state, parent = rule
        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2
        if (num1) > num_prefixes:
            ref[num1 - 1] = int(num2)

    ref = ref[num_prefixes:]
    ref = ref.tolist()

    ed = evaluateEditDistance.edit(ref, hyp)

    if (ed < sat_threshold):
        is_compliant = True
    else:
        is_compliant = False

    label = generate_label(trace, labeling)

    if is_compliant:
        cm = ConfusionMatrix.TP if label == TraceLabel.TRUE else ConfusionMatrix.FP
    else:
        cm = ConfusionMatrix.FN if label == TraceLabel.TRUE else ConfusionMatrix.TN

    return is_compliant, cm


# Definisci una funzione per testare il decision tree
def test_dt(test_log, train_log, labeling, prefixing, support_threshold, checkers, rules):

    (frequent_events, frequent_pairs) = generate_frequent_events_and_pairs(train_log, support_threshold)

    print("Generazione dell'input per il decision tree ...")
    dt_input = Encoding(train_log, labeling)
    dt_input.encode_traces

    print("Generazione del decision tree ...")
    return dt_score(dt_input=dt_input)

# Definisci una classe ParamsOptimizer per ottimizzare i parametri del modello
class ParamsOptimizer:
    def __init__(self, data_log, train_val_log, val_log, train_log, parameters, labeling, checkers, rules, min_prefix_length, max_prefix_length):
        # Inizializza i parametri per l'ottimizzazione
        self.parameter_names = parameters.keys()
        self.val_log = val_log
        self.data_log = data_log
        self.train_val_log = train_val_log
        self.param_grid = [element for element in itertools.product(*parameters.values())]
        self.train_log = train_log
        self.parameters = parameters
        self.labeling = labeling
        self.checkers = checkers
        self.rules = rules
        self.model_grid = []
        self.min_prefix_length = min_prefix_length
        self.max_prefix_length = max_prefix_length

    # Metodo per eseguire una ricerca dei parametri nel grid
    def params_grid_search(self, dataset_name, constr_family):
        categories = [TraceLabel.FALSE.value, TraceLabel.TRUE.value]

        for param_id, param_tuple in enumerate(self.param_grid):
            model_dict = {'dataset_name': dataset_name, 'constr_family': constr_family, 'parameters': param_tuple,
                          'f1_score_val': None, 'f1_score_train': None, 'f1_prefix_val': None, 'max_depth': 0,
                          'id': param_id, 'model': None, 'frequent_events': None, 'frequent_pairs': None}

            (frequent_events_train, frequent_pairs_train) = generate_frequent_events_and_pairs(self.data_log,
                                                                                               param_tuple[0])

            # Genera l'input per il decision tree
            dt_input_train = Encoding(self.train_log, labeling=self.labeling)
            dt_input_train.encode_traces
            dt_input_val = Encoding(self.val_log, labeling=self.labeling)
            dt_input_val.encode_traces

            X_train = pd.DataFrame(dt_input_train.encoded_data, columns=dt_input_train.features)
            y_train = pd.Categorical(dt_input_train.labels, categories=categories)

            X_val = pd.DataFrame(dt_input_val.encoded_data, columns=dt_input_val.features)
            y_val = pd.Categorical(dt_input_val.labels, categories=categories)

            # Genera il decision tree e calcola il punteggio su un set di validazione
            dtc, f1_score_val, f1_score_train = generate_decision_tree(X_train, X_val, y_train, y_val,
                                                                      class_weight=param_tuple[1],
                                                                      min_samples_split=param_tuple[2])
            paths = generate_paths(dtc=dtc, dt_input_features=dt_input_train.features, target_label=self.labeling["target"])

            # Valutazione su set di validazione
            results = []
            for pref_id, prefix_len in enumerate(range(self.min_prefix_length, self.max_prefix_length + 1)):
                prefixing = {
                    "type": PrefixType.ONLY,
                    "length": prefix_len
                }

                evaluation = evaluate_recommendations(input_log=self.val_log,
                                                      labeling=self.labeling, prefixing=prefixing,
                                                      rules=self.rules, paths=paths)
                results.append(evaluation)

            model_dict['model'] = dtc
            model_dict['f1_score_val'] = f1_score_val
            model_dict['f1_score_train'] = f1_score_train
            model_dict['f1_prefix_val'] = np.average([res.fscore for res in results])
            model_dict['frequent_events'] = frequent_events_train
            model_dict['frequent_pairs'] = frequent_pairs_train
            self.model_grid.append(model_dict)

        # Retraining del DT utilizzando il set train_val con i migliori parametri testati sul set di validazione
        sorted_models = sorted(self.model_grid, key=lambda d: d['f1_prefix_val'])
        best_model_dict = sorted_models[-1]

        dt_input_trainval = Encoding(self.train_val_log, labeling=self.labeling)
        dt_input_trainval.encode_traces
        dt_input_val = Encoding(self.val_log, labeling=self.labeling)
        dt_input_val.encode_traces

        X_train_val = pd.DataFrame(dt_input_trainval.encoded_data, columns=dt_input_trainval.features)
        y_train_val = pd.Categorical(dt_input_trainval.labels, categories=categories)
        X_val = pd.DataFrame(dt_input_val.encoded_data, columns=dt_input_val.features)
        y_val = pd.Categorical(dt_input_val.labels, categories=categories)

        dtc, _, _ = generate_decision_tree(X_train_val, X_val, y_train_val, y_val,
                                           class_weight=best_model_dict['parameters'][1],
                                           min_samples_split=best_model_dict['parameters'][2])

        return dtc


# Definisci una funzione per generare le raccomandazioni basate su un percorso
def recommend(prefix, path, dt_input_trainval):
    recommendation = ""

    prefixes = []
    for trace in prefix:
        prefixes.append(trace['concept:name'])

    num_prefixes = len(prefixes)

    for rule in path.rules:
        feature, state, parent = rule

        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2

        if (num1) > num_prefixes:
            rec = np.zeros(num1, dtype=int)
            rec[num1 - 1] = int(num2)
            rec = rec.tolist()

            rec_str = dt_input_trainval.decode(rec)
            for column in rec_str.columns:
                if (rec_str[column].iloc[0] != '0') and rec_str[column].notnull().any():
                    if state == TraceState.VIOLATED:
                        recommendation += "" + column + " should not be " + rec_str[column].iloc[0] + "; "
                    if state == TraceState.SATISFIED:
                        recommendation += "" + column + " should be " + rec_str[column].iloc[0] + "; "

    return recommendation

# Definisci una funzione per valutare se una traccia è conforme o meno
def evaluate(trace, path, num_prefixes, dt_input_trainval, sat_threshold, labeling):
    is_compliant = True
    activities = []

    for idx, event in enumerate(trace):
        for attribute_key, attribute_value in event.items():
            if (attribute_key == 'concept:name'):
                activities.append(attribute_value)

    activities = dt_input_trainval.encode(activities)

    hyp = []
    hypInt = []
    for column in activities.columns:
        hyp.extend(activities[column].values)
    hyp = np.array(hyp)
    hyp = hyp.tolist()

    for value in hyp:
        if isinstance(value, str) and value.isdigit():
            hypInt.append(int(value))
    if len(hypInt) > 0:
        hyp = copy.deepcopy(hypInt)

    hyp = hyp[num_prefixes:]

    n_max = 0

    for rule in path.rules:
        feature, state, parent = rule
        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2
        if (num1 > n_max):
            n_max = num1

    ref = np.zeros(n_max, dtype=int)

    for rule in path.rules:
        feature, state, parent = rule

        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2
        if (num1) > num_prefixes:
            ref[num1 - 1] = int(num2)

    ref = ref[num_prefixes:]
    ref = ref.tolist()

    ed = evaluateEditDistance.edit(ref, hyp)

    if (ed < sat_threshold):
        is_compliant = True
    else:
        is_compliant = False

    label = generate_label(trace, labeling)

    if is_compliant:
        cm = ConfusionMatrix.TP if label == TraceLabel.TRUE else ConfusionMatrix.FP
    else:
        cm = ConfusionMatrix.FN if label == TraceLabel.TRUE else ConfusionMatrix.TN

    return is_compliant, cm

# Definisci una funzione per testare il decision tree e ottenere raccomandazioni ed evalutation
def test_dt(test_log, train_log, labeling, prefixing, support_threshold, checkers, rules):

    (frequent_events, frequent_pairs) = generate_frequent_events_and_pairs(train_log, support_threshold)

    print("Generazione dell'input per il decision tree ...")
    dt_input = Encoding(train_log, labeling)
    dt_input.encode_traces

    print("Generazione del decision tree ...")
    return dt_score(dt_input=dt_input)


def train_path_recommender(data_log, train_val_log, val_log, train_log, labeling, support_threshold,
                           dataset_name, output_dir, dt_input_trainval):
    if labeling["threshold_type"] == LabelThresholdType.LABEL_MEAN:
        labeling["custom_threshold"] = calc_mean_label_threshold(train_log, labeling)

    target_label = labeling["target"]

    # Stampa un messaggio
    print("Generazione dell'albero decisionale con l'ottimizzazione dei parametri ...")

    # Se impostato, trova il miglior modello decisionale
    if settings.optmize_dt:
        best_model_dict, feature_names = find_best_dt(dataset_name, train_val_log,
                                                      support_threshold, settings.print_dt, dt_input_trainval)
    # Altrimenti, esegui l'ottimizzazione dei parametri
    # else:
    #     param_opt = ParamsOptimizer(data_log, train_val_log, val_log, train_log, settings.hyperparameters, labeling,
    #                                 checkers, rules, min_prefix_length, max_prefix_length)
    #     best_model_dict, feature_names = param_opt.params_grid_search(dataset_name, constr_family)

    # Scrivi i parametri del miglior modello su un file CSV
    with open(os.path.join(output_dir, 'model_params.csv'), 'a') as f:
        w = csv.writer(f, delimiter='\t')
        row = list(best_model_dict.values())
        w.writerow(row[:-1])  # Non stampare il modello stesso

    # Stampa un messaggio
    print("Generazione dei percorsi dell'albero decisionale ...")

    # Genera i percorsi dell'albero decisionale
    paths = generate_paths(dtc=best_model_dict['model'], dt_input_features=feature_names,
                           target_label=target_label)
    return paths, best_model_dict


def evaluate_recommendations(input_log, labeling, prefixing, rules, paths):
    # if labeling["threshold_type"] == LabelThresholdType.LABEL_MEAN:
    #    labeling["custom_threshold"] = calc_mean_label_threshold(train_log, labeling)

    target_label = labeling["target"]

    # Stampa un messaggio
    print("Generazione dei prefissi di test ...")

    # Genera i prefissi di test
    prefixes = generate_prefixes(input_log, prefixing)

    eval_res = EvaluationResult()

    for prefix_length in prefixes:
        # for id, pref in enumerate(prefixes[prefix_length]): print(id, input_log[pref.trace_num][0]['label'])
        for prefix in prefixes[prefix_length]:
            for path in paths:
                path.fitness = calcPathFitnessOnPrefix(prefix.events, path, rules, settings.fitness_type)

            # Ordina i percorsi in base al fitness
            paths = sorted(paths, key=lambda path: (- path.fitness, path.impurity, - path.num_samples["total"]),
                           reverse=False)

            selected_path = None

            for path_index, path in enumerate(paths):

                if selected_path and (
                        path.fitness != selected_path.fitness or path.impurity != selected_path.impurity or path.num_samples != selected_path.num_samples):
                    break

                recommendation = recommend(prefix.events, path, rules)
                # print(f"{prefix_length} {prefix.trace_num} {prefix.trace_id} {path_index}->{recommendation}")
                trace = input_log[prefix.trace_num]

                if recommendation != "Contradiction" and recommendation != "":
                    # if recommendation != "":
                    selected_path = path
                    trace = input_log[prefix.trace_num]
                    is_compliant, e = evaluate(trace, path, rules, labeling)

                    """
                    if prefix_length > 2:
                        # for event in prefix.events: print(event['concept:name'])
                        # for path in paths: print(path.rules)
                        #recommend(prefix.events, paths[0], rules)
                        #len(paths[0])
                        #for rule in paths[0]: print(rule)
                        for path in paths: print(evaluate(trace, path, rules, labeling))
                    """

                    if e == ConfusionMatrix.TP:
                        eval_res.tp += 1
                    elif e == ConfusionMatrix.FP:
                        eval_res.fp += 1
                    elif e == ConfusionMatrix.FN:
                        eval_res.fn += 1
                    elif e == ConfusionMatrix.TN:
                        eval_res.tn += 1

    try:
        eval_res.precision = eval_res.tp / (eval_res.tp + eval_res.fp)
    except ZeroDivisionError:
        eval_res.precision = 0

    try:
        eval_res.recall = eval_res.tp / (eval_res.tp + eval_res.fn)
    except ZeroDivisionError:
        eval_res.recall = 0

    try:
        eval_res.fscore = 2 * eval_res.precision * eval_res.recall / (eval_res.precision + eval_res.recall)
    except ZeroDivisionError:
        eval_res.fscore = 0

    return eval_res


def train_path_recommender(data_log, train_val_log, val_log, train_log, labeling, support_threshold,
                           dataset_name, output_dir, dt_input_trainval):
    if labeling["threshold_type"] == LabelThresholdType.LABEL_MEAN:
        labeling["custom_threshold"] = calc_mean_label_threshold(train_log, labeling)

    target_label = labeling["target"]

    # Stampa un messaggio
    print("Generazione dell'albero decisionale con l'ottimizzazione dei parametri ...")

    # Se impostato, trova il miglior modello decisionale
    if settings.optmize_dt:
        best_model_dict, feature_names = find_best_dt(dataset_name, train_val_log,
                                                      support_threshold, settings.print_dt, dt_input_trainval)
    # Altrimenti, esegui l'ottimizzazione dei parametri
    # else:
    #     param_opt = ParamsOptimizer(data_log, train_val_log, val_log, train_log, settings.hyperparameters, labeling,
    #                                 checkers, rules, min_prefix_length, max_prefix_length)
    #     best_model_dict, feature_names = param_opt.params_grid_search(dataset_name, constr_family)

    # Scrivi i parametri del miglior modello su un file CSV
    with open(os.path.join(output_dir, 'model_params.csv'), 'a') as f:
        w = csv.writer(f, delimiter='\t')
        row = list(best_model_dict.values())
        w.writerow(row[:-1])  # Non stampare il modello stesso

    # Stampa un messaggio
    print("Generazione dei percorsi dell'albero decisionale ...")

    # Genera i percorsi dell'albero decisionale
    paths = generate_paths(dtc=best_model_dict['model'], dt_input_features=feature_names,
                           target_label=target_label)
    return paths, best_model_dict


def evaluate_recommendations(input_log, labeling, prefixing, rules, paths):
    # if labeling["threshold_type"] == LabelThresholdType.LABEL_MEAN:
    #    labeling["custom_threshold"] = calc_mean_label_threshold(train_log, labeling)

    target_label = labeling["target"]

    # Stampa un messaggio
    print("Generazione dei prefissi di test ...")

    # Genera i prefissi di test
    prefixes = generate_prefixes(input_log, prefixing)

    eval_res = EvaluationResult()

    for prefix_length in prefixes:
        # for id, pref in enumerate(prefixes[prefix_length]): print(id, input_log[pref.trace_num][0]['label'])
        for prefix in prefixes[prefix_length]:
            for path in paths:
                path.fitness = calcPathFitnessOnPrefix(prefix.events, path, rules, settings.fitness_type)

            # Ordina i percorsi in base al fitness
            paths = sorted(paths, key=lambda path: (- path.fitness, path.impurity, - path.num_samples["total"]),
                           reverse=False)

            selected_path = None

            for path_index, path in enumerate(paths):

                if selected_path and (
                        path.fitness != selected_path.fitness or path.impurity != selected_path.impurity or path.num_samples != selected_path.num_samples):
                    break

                recommendation = recommend(prefix.events, path, rules)
                # print(f"{prefix_length} {prefix.trace_num} {prefix.trace_id} {path_index}->{recommendation}")
                trace = input_log[prefix.trace_num]

                if recommendation != "Contradiction" and recommendation != "":
                    # if recommendation != "":
                    selected_path = path
                    trace = input_log[prefix.trace_num]
                    is_compliant, e = evaluate(trace, path, rules, labeling)

                    """
                    if prefix_length > 2:
                        # for event in prefix.events: print(event['concept:name'])
                        # for path in paths: print(path.rules)
                        #recommend(prefix.events, paths[0], rules)
                        #len(paths[0])
                        #for rule in paths[0]: print(rule)
                        for path in paths: print(evaluate(trace, path, rules, labeling))
                    """

                    if e == ConfusionMatrix.TP:
                        eval_res.tp += 1
                    elif e == ConfusionMatrix.FP:
                        eval_res.fp += 1
                    elif e == ConfusionMatrix.FN:
                        eval_res.fn += 1
                    elif e == ConfusionMatrix.TN:
                        eval_res.tn += 1

    try:
        eval_res.precision = eval_res.tp / (eval_res.tp + eval_res.fp)
    except ZeroDivisionError:
        eval_res.precision = 0

    try:
        eval_res.recall = eval_res.tp / (eval_res.tp + eval_res.fn)
    except ZeroDivisionError:
        eval_res.recall = 0

    try:
        eval_res.fscore = 2 * eval_res.precision * eval_res.recall / (eval_res.precision + eval_res.recall)
    except ZeroDivisionError:
        eval_res.fscore = 0

    return eval_res
