from src.enums.ConstraintChecker import ConstraintChecker
from src.enums import TraceState
from src.constants.constants import CONSTRAINT_CHECKER_FUNCTIONS
from src.models.Prefix import *
from src.machine_learning.encoding import *
from src.machine_learning.apriori import generate_frequent_events_and_pairs
#from src.machine_learning.decision_tree import generate_decision_tree, generate_paths, generate_boost_decision_tree
from src.enums import PrefixType
from src.machine_learning import fitnessEditDistance
from sklearn.model_selection import train_test_split
import itertools
from src.enums import TraceLabel
import pandas as pd
import numpy as np
from src.machine_learning.encoding.Encoding_setting import trace_attributes, resource_attributes
import settings
import math
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

# Definizione della funzione `extract_numbers_from_string` per l'estrazione dei numeri da una stringa
def extract_numbers_from_string(input_string, log, trace_attributes_for_numb, resource_attributes_for_numb, excluded_attributes):
    # Filtra trace_attributes per il log specifico, escludendo gli attributi non desiderati
    trace_attributes_for_log = [
        attribute for attribute in trace_attributes_for_numb.get(log, [])
        if attribute not in excluded_attributes
    ]

    # Filtra resource_attributes per il log specifico, escludendo gli attributi non desiderati
    resource_attributes_for_log = [
        attribute for attribute in resource_attributes_for_numb.get(log, [])
        if attribute not in excluded_attributes
    ]

    # Controlla il pattern "prefix"
    prefix_pattern = r"prefix_(\d+)_(\d+)"
    matches = re.findall(prefix_pattern, input_string)
    if matches:
        numbers = [(int(match[0]), int(match[1])) for match in matches]
        return numbers

    # Controlla i pattern in trace_attributes_for_log
    for attribute in trace_attributes_for_log:
        trace_pattern = rf"{attribute}_(\d+)"
        matches = re.findall(trace_pattern, input_string)
        if matches:
            numbers = [(int(match[0]), int(match[1])) for match in matches]
            return numbers

    # Controlla i pattern in resource_attributes_for_log
    for attribute in resource_attributes_for_log:
        resource_pattern = rf"{attribute}_(\d+)_(\d+)"
        matches = re.findall(resource_pattern, input_string)
        if matches:
            numbers = [(int(match[0]), int(match[1])) for match in matches]
            return numbers
    # Nessuna corrispondenza trovata
    return None



# Definizione della funzione `calcPathFitnessOnPrefix` per il calcolo della fitness del percorso su un prefisso
def calcPathFitnessOnPrefix(prefix, path, dt_input_trainval):

    prefixes = []
    for trace in prefix:
        prefixes.append(trace['concept:name'])

    num_prefixes = len(prefixes)

    prefixes = dt_input_trainval.encode(prefixes)

    hyp = []
    for column in prefixes.columns:
        hyp.extend(prefixes[column].values)
    hyp = np.array(hyp)
    hyp = hyp.tolist()

    rec = np.zeros(len(hyp), dtype=int)
    ref = rec.tolist()

    for rule in path.rules:
        feature, state, parent = rule

        numbers = extract_numbers_from_string(feature)
        for n1, n2 in numbers:
            num1 = n1
            num2 = n2

        if num1 >= num_prefixes:
            continue

        if state == TraceState.VIOLATED:
            if isinstance(ref[num1 - 1], list):
                ref[num1 - 1].append(-num2)
            else:
                ref[num1 - 1] = [-num2]
        else:
            ref[num1 - 1] = int(num2)

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
