from src.enums.ConstraintChecker import ConstraintChecker
from src.enums import TraceState
from src.constants.constants import CONSTRAINT_CHECKER_FUNCTIONS
from src.models.Prefix import *
from src.machine_learning.encoding import *
from src.machine_learning.apriori import generate_frequent_events_and_pairs
#from src.machine_learning.decision_tree import generate_decision_tree, generate_paths, generate_boost_decision_tree
from src.enums import PrefixType
from src.machine_learning import fitnessEditDistance,filter_attributes
from sklearn.model_selection import train_test_split
import itertools
from src.enums import TraceLabel
from src.machine_learning.encoding.Encoding_setting import trace_attributes, resource_attributes
from pm4py.objects.conversion.log import converter as log_converter
import settings
import math
import pandas as pd
import numpy as np
import re

trace_attributes_for_numb=trace_attributes
resource_attributes_for_numb=resource_attributes
# Definizione della funzione `gain` per il calcolo del guadagno
def gain(c, nc, pc, pnc):
    prob_pos_comp = (pc + settings.smooth_factor) / (c + settings.smooth_factor * settings.num_classes)
    prob_pos_non_comp = (pnc + settings.smooth_factor) / (nc + settings.smooth_factor * settings.num_classes)
    _gain = prob_pos_comp / prob_pos_non_comp
    return _gain

# Definizione della funzione `matthews_corrcoef` per il calcolo del coefficiente di correlazione di Matthews
def matthews_corrcoef(tp, fp, fn, tn):
    num = tp * tn - fp * fn
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denom == 0:
        return 0
    else:
        return num / denom

# Definizione della funzione `calcScore` per il calcolo dello score
def calcScore(path, pos_paths_total_samples_, weights):
    purity = 1 - path.impurity
    pos_probability = path.num_samples['positive'] / pos_paths_total_samples_
    w = np.array([0.8, 0.1, 0.1])
    w = np.array([0.0, 0, 0])

    if path.num_samples['node_samples'] > 2:
        w = weights

    return np.mean(w * np.array([path.fitness, purity, pos_probability]))

# Definizione della funzione `calcPathFitnessOnPrefixGOOD` per il calcolo della fitness del percorso su un prefisso
def calcPathFitnessOnPrefixGOOD(prefix, path, rules, fitness_type):
    path_weights = []
    path_activated_rules = np.zeros(len(path.rules))
    fitness = None
    for rule_idx, rule in enumerate(path.rules):
        template, rule_state, _ = rule
        template_name, template_params = parse_method(template)

        result = None
        if template_name in [ConstraintChecker.EXISTENCE.value, ConstraintChecker.ABSENCE.value, ConstraintChecker.INIT.value, ConstraintChecker.EXACTLY.value]:
            result = CONSTRAINT_CHECKER_FUNCTIONS[template_name](prefix, True, template_params[0], rules)
        else:
            result = CONSTRAINT_CHECKER_FUNCTIONS[template_name](prefix, True, template_params[0], template_params[1], rules)

        if rule_state == result.state:
            path_activated_rules[rule_idx] = 1
        path_weights.append(1 / (rule_idx + 1))

    if fitness_type == 'mean':
        fitness = np.mean(path_activated_rules)
    elif fitness_type == 'wmean':
        fitness = np.sum(path_weights * path_activated_rules) / np.sum(path_weights)

    return fitness


def extract_index_from_feature(feature, features, resource_atts, trace_atts):
    # Assicurati che resource_atts e trace_atts siano liste
    if isinstance(resource_atts, str):
        resource_atts = [resource_atts]
    if isinstance(trace_atts, str):
        trace_atts = [trace_atts]

    # Pattern per prefix e resource_atts
    pattern_prefix_resource = fr'^(prefix|{"|".join(map(re.escape, resource_atts))})_(\d+)_\d+'
    # Pattern per trace_atts
    pattern_trace = fr'^({"|".join(map(re.escape, trace_atts))})_(\d+)'

    match_prefix_resource = re.search(pattern_prefix_resource, feature)
    match_trace = re.search(pattern_trace, feature)

    if match_prefix_resource:
        key = match_prefix_resource.group(0).rsplit('_', 1)[0]  # Ottieni prefix_num1 o resource_att_num1
        for i, feat in enumerate(features):
            if feat.startswith(key):
                return i + 1  # +1 per allineare all'indicizzazione a base 1

    if match_trace:
        key_prefix = match_trace.group(1)  # Ottieni il prefisso trace_att
        key_number = match_trace.group(2)  # Ottieni solo il numero
        for i, feat in enumerate(features):
            if feat.startswith(key_prefix) and feat.endswith(f'_{key_number}'):
                return i + 1  # +1 per allineare all'indicizzazione a base 1

    return None

# Definizione della funzione `extract_numbers_from_string` per l'estrazione dei numeri da una stringa
def extract_numbers_from_string(input_string, trace_att_d, resource_att_d):
    # Define the patterns for different types of encodings
    patterns = {
        "prefix": "prefix_(\\d+)_(\\d+)",
        "trace_att": [f"{trace_name}_(\\d+)" for trace_name in trace_att_d],
        "resource_att": [f"{resource_name}_(\\d+)_(\\d+)" for resource_name in resource_att_d]
    }

    result = {
        "trace_att": [],
        "prefix": [],
        "resource_att": []
    }

    # Extract trace attributes
    for pattern in patterns["trace_att"]:
        matches = re.findall(pattern, input_string)
        if matches:
            for match in matches:
                result["trace_att"].append(int(match))

    # Extract prefixes
    matches = re.findall(patterns["prefix"], input_string)
    if matches:
        for match in matches:
            result["prefix"].append((int(match[0]), int(match[1])))

    # Extract resource attributes
    for pattern in patterns["resource_att"]:
        matches = re.findall(pattern, input_string)
        if matches:
            for match in matches:
                result["resource_att"].append((int(match[0]), int(match[1])))

    # Flatten the result into a single list of tuples
    flattened_result = result["prefix"] + result["resource_att"] + [(num,) for num in result["trace_att"]]

    return flattened_result if flattened_result else None

# Definizione della funzione `calcPathFitnessOnPrefix` per il calcolo della fitness del percorso su un prefisso
def calcPathFitnessOnPrefix(prefix, path, dt_input_trainval, log, dataset_name, features):
    trace_att_d, resource_att_d = filter_attributes.get_attributes_by_dataset(dataset_name)
    features = features[1:]
    prefixes = []
    for trace in prefix:
        prefixes.append(trace['concept:name'])

    num_prefixes = len(prefixes)

    prefixes = dt_input_trainval.encode(prefixes,features)

    hyp = [None] * len(features)
    for column in prefixes.columns:
        # Troviamo l'indice della colonna in 'features'
        if column in features:
            index = features.index(column)
            values = prefixes[column].values
            for i, value in enumerate(values):
                if hyp[index] is None:
                    hyp[index] = [None] * len(values)
                hyp[index][i] = value
    hyp = [item for sublist in hyp for item in (sublist if isinstance(sublist, list) else [sublist])]
    hyp = np.array(hyp, dtype=object)
    hyp = hyp.tolist()

    rec = np.zeros(len(hyp), dtype=int)
    ref = rec.tolist()

    for rule in path.rules:
        feature, state, parent = rule

        numbers = extract_numbers_from_string(feature,trace_att_d,resource_att_d)
        if numbers:
            for num_tuple in numbers:
                if len(num_tuple) == 2:
                    num1, num2 = num_tuple
                else:
                    num1 = num_tuple[0]
                    num2 = None

                if num1 >= num_prefixes or num1 <= 0:
                    continue

                feature_index = extract_index_from_feature(feature, features,trace_att_d,resource_att_d)

                if state == TraceState.VIOLATED:
                    if isinstance(ref[feature_index], list):
                        if num2 is not None:
                            ref[feature_index].append(-num2)
                    else:
                        ref[feature_index] = [-num2] if num2 is not None else ref[feature_index]
                else:
                    ref[feature_index] = int(num2) if num2 is not None else ref[feature_index]

    return fitnessEditDistance.edit(ref, hyp)

# Definizione della funzione `generate_prefixes` per la generazione dei prefissi
def generate_prefixes(log, prefixing):
    def only(n):
        prefixes = {n: []}
        for index, trace in enumerate(log):
            if len(trace) >= n:
                events = []
                for event in trace:
                    events.append(event)
                    if len(events) == n:
                        prefix_model = Prefix(trace.attributes["concept:name"], index, events.copy())
                        prefixes[n].append(prefix_model)
                        break

        return prefixes

    def up_to(n):
        prefixes = {"UPTO": []}
        for index, trace in enumerate(log):
            events = []
            for event in trace:
                events.append(event)
                prefix_model = Prefix(trace.attributes["concept:name"], index, events.copy())
                prefixes["UPTO"].append(prefix_model)
                if len(events) == n:
                    break
        return prefixes

    n = prefixing["length"]
    if prefixing["type"] == PrefixType.ONLY:
        return only(n)
    else:
        return up_to(n)

# Definizione della funzione `parse_method` per il parsing di un metodo
def parse_method(method):
    method_name = method.split("[")[0]
    rest = method.split("[")[1][:-1]
    if "," in rest:
        method_params = rest.split(",")
    else:
        method_params = [rest]
    return method_name, method_params

# Definizione della funzione `generate_prefix_path` per la generazione del percorso del prefisso
def generate_prefix_path(prefix):
    current_prefix = ""
    for event in prefix:
        current_prefix += event["concept:name"] + ", "
    current_prefix = current_prefix[:-2]
    return current_prefix

# Definizione della funzione `generate_rules` per la generazione delle regole
def generate_rules(rules):
    if rules.strip() == "":
        rules = "True"
        return rules
    if "is" in rules:
        rules = rules.replace("is", "==")
    words = rules.split()
    for index, word in enumerate(words):
        if "A." in word:
            words[index] = "A[\"" + word[2:] + "\"]"
            if not words[index + 2].isdigit():
                words[index + 2] = "\"" + words[index + 2] + "\""
        elif "T." in word:
            words[index] = "T[\"" + word[2:] + "\"]"
            if not words[index + 2].isdigit():
                words[index + 2] = "\"" + words[index + 2] + "\""
        elif word == "same":
            words[index] = "A[\"" + words[index + 1] + \
                "\"] == T[\"" + words[index + 1] + "\"]"
            words[index + 1] = ""
    words = list(filter(lambda word: word != "", words))
    rules = " ".join(words)
    return rules

def rename_and_convert_to_log(df, dataset_manager):
    renamed_df = df.rename(
        columns={
            dataset_manager.timestamp_col: 'time:timestamp',
            dataset_manager.case_id_col: 'case:concept:name',
            dataset_manager.activity_col: 'concept:name'
        }
    )
    return log_converter.apply(renamed_df)


def find_feature_position(feature, features):
    # Split the feature by underscores and take the first two parts
    feature_base = '_'.join(feature.split('_')[:2])

    # Check if the base feature is in the features list
    if feature_base in features:
        # Return the position (index) of the found feature
        return features.index(feature_base)
