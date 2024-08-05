from src.enums.ConstraintChecker import ConstraintChecker
from Colorlib.Colors import *
import os


def read_options_from_dat(filepath):
    options = {}
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                if value.lower() in ['true', 'false']:
                    options[key] = value.lower() == 'true'
                elif value == '0%':
                    options[key] = 0.0
                elif value.endswith('%') and value[:-1].replace('.', '', 1).isdigit():
                    options[key] = float(value[:-1])
                elif value.replace('.', '', 1).isdigit():
                    options[key] = float(value) if '.' in value else int(value)
                elif key == 'excluded_attributes':
                    options[key] = value.split(',')
                else:
                    options[key] = value
    return options


def read_datasets_from_dat(filepath):
    datasets_names = []
    with open(filepath, 'r') as file:
        for line in file:
            dataset_name = line.replace('"', '').replace(',', '').strip()
            if dataset_name:
                datasets_names.append(dataset_name)
    return datasets_names


# ========================================paths=========================================================================


options_filepath = 'Option.dat'
datasets_names_filepath = 'Datasets_names.dat'
dataset_debug = 'Dataset_name.txt'
encoding_path = 'Encoding.dat'


# ========================================encoding_selection============================================================

def read_type_encoding(filepath):
    with open(filepath, 'r') as file:
        type_encoding = file.readline().strip()
    return type_encoding


type_encoding = read_type_encoding(encoding_path) if read_type_encoding(encoding_path) else 'simple'
# simple, frequency, complex


# ================================================== datasets_names ====================================================


datasets_names = read_datasets_from_dat(datasets_names_filepath) if read_datasets_from_dat(
    datasets_names_filepath) else read_datasets_from_dat(dataset_debug)
options = read_options_from_dat(options_filepath)

# ================================================= thresholds =========================================================


support_threshold_dict = {'min': 0.05, 'max': 1.75}

smooth_factor = options['smooth_factor']    if options['smooth_factor'] else 1
num_classes =   options['num_classes']      if options['num_classes']   else 2
sat_threshold = options['sat_threshold']    if options['sat_threshold'] else 0.75
top_K_paths =   options['top_K_paths']      if options['top_K_paths']   else 6

reranking =         options['reranking']        if options['reranking']         else False
cumulative_res =    options['cumulative_res']   if options['cumulative_res']    else False
optimize_dt =       options['optimize_dt']      if options['optimize_dt']       else True
compute_gain =      options['compute_gain']     if options['compute_gain']      else False
train_prefix_log =  options['train_prefix_log'] if options['train_prefix_log']  else False
one_hot_encoding =  options['one_hot_encoding'] if options['one_hot_encoding']  else False
use_score =         options['use_score']        if options['use_score']         else True
compute_baseline =  options['compute_baseline'] if options['compute_baseline']  else False

fitness_type =  options['fitness_type'] if options['fitness_type']  else 'mean'  # wmean
sat_type =      options['sat_type']     if options['sat_type']      else 'count_occurrences'

excluded_attributes = options['excluded_attributes'] if options[
    'excluded_attributes'] else 'concept:name,time:timestamp,label,Case ID'

selected_evaluation_edit_distance = (
    'edit_distance_lib' if not options['selected_evaluation_edit_distance'] or type_encoding == "simple" else options[
        'selected_evaluation_edit_distance'])
# ['edit_distance_lib', 'edit_distance_separate','weighted_edit_distance']


# ========================================= Debugging rules ============================================================


print_dt =              options['print_dt']             if options['print_dt']              else True
Print_edit_distance =   options['Print_edit_distance']  if options['Print_edit_distance']   else False
print_log =             options['print_log']            if options['print_log']             else False
print_length =          options['print_length']         if options['print_length']          else False
eval_stamp =            options['eval_stamp']           if options['eval_stamp']            else False
recc_stamp =            options['recc_stamp']           if options['recc_stamp']            else False
Allprint =              options['Allprint']             if options['Allprint']              else False
enable_log =            options['enable_log']           if options['enable_log']            else False

quick = options['Quick'] if options['Quick'] else False


# ======================================== Rule_of_prefix ==============================================================
weighted_prefix_generation = options['weighted_prefix_generation'] if options['weighted_prefix_generation'] else False
if quick:
    if weighted_prefix_generation:
        ruleprefix = "QW"
    else:
        ruleprefix = "QN"
else:
    if weighted_prefix_generation:
        ruleprefix = "W"
    else:
        ruleprefix = "N"

# ======================================== weights =====================================================================

# weights of the three components of the encoding
temp_wtrace_att =       options['wtrace_att']       if options['wtrace_att']    else 0
temp_wactivities =      options['wactivities']      if options['wactivities']   else 0
temp_wresource_att =    options['wresource_att']    if options['wresource_att'] else 0

# Calcola la somma dei valori temporanei
total = temp_wtrace_att + temp_wactivities + temp_wresource_att
try:
    if total > 100:
        raise ValueError("Total percentage must be less than or equal to 100%")
except ValueError as e:
    print(e)

# Se la somma è inferiore a 1.0 o diverso da 33%, arrotonda il valore più grande per ottenere 1.0
if not (temp_wresource_att == temp_wtrace_att == temp_wactivities == 0.33):
    if total < 100:
        max_value = max(temp_wtrace_att, temp_wactivities, temp_wresource_att)
        increment_remaining = (100 - total)

        if temp_wtrace_att == temp_wactivities == temp_wresource_att:
            increment = increment_remaining / 3
            temp_wtrace_att += increment
            temp_wactivities += increment
            temp_wresource_att += increment

            if temp_wtrace_att + temp_wactivities + temp_wresource_att < 100:
                temp_wtrace_att += 1
        elif temp_wtrace_att == temp_wactivities and temp_wtrace_att > temp_wresource_att:
            increment = increment_remaining / 2
            temp_wtrace_att += increment
            temp_wactivities += increment

            if temp_wtrace_att + temp_wactivities + temp_wresource_att < 100:
                temp_wresource_att += 1
        elif temp_wtrace_att == temp_wresource_att and temp_wtrace_att > temp_wactivities:
            increment = increment_remaining / 2
            temp_wtrace_att += increment
            temp_wresource_att += increment

            if temp_wtrace_att + temp_wactivities + temp_wresource_att < 100:
                temp_wactivities += 1
        elif temp_wactivities == temp_wresource_att and temp_wactivities > temp_wtrace_att:
            increment = increment_remaining / 2
            temp_wactivities += increment
            temp_wresource_att += increment

            if temp_wtrace_att + temp_wactivities + temp_wresource_att < 100:
                temp_wtrace_att += 1
        else:
            if max_value == temp_wtrace_att:
                temp_wtrace_att += increment_remaining
            elif max_value == temp_wactivities:
                temp_wactivities += increment_remaining
            else:
                temp_wresource_att += increment_remaining

# Aggiorna le opzioni con i nuovi valori
wtrace_att = temp_wtrace_att
wactivities = temp_wactivities
wresource_att = temp_wresource_att

# ========================================= folders ====================================================================


output_dt_dir_base = "media/output/dt/"
if ruleprefix == "N":
    output_dt_dir_rp = os.path.join(output_dt_dir_base, "/N")
elif ruleprefix == "W":
    output_dt_dir_rp = os.path.join(output_dt_dir_base, "/W")
elif ruleprefix == "QN":
    output_dt_dir_rp = os.path.join(output_dt_dir_base, "/QN")
elif ruleprefix == "QW":
    output_dt_dir_rp = os.path.join(output_dt_dir_base, "/QW")
if not os.path.exists(output_dt_dir_rp):
    os.makedirs(output_dt_dir_rp)


output_dt_dir_s = os.path.join(output_dt_dir_rp, "/simple")
output_dt_dir_cl = os.path.join(output_dt_dir_rp, "/complex/lib")
output_dt_dir_cc = os.path.join(output_dt_dir_rp, "/complex/code")
output_dt_dir_cw = os.path.join(output_dt_dir_rp, "/complex/weighted")


if type_encoding == "simple":
    output_dir = output_dt_dir_s
    print(f"{BLUE} Using {output_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "weighted_edit_distance":
    output_dir = output_dt_dir_cw
    print(f"{BLUE} Using {output_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "edit_distance_lib":
    output_dir = output_dt_dir_cl
    print(f"{BLUE} Using {output_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "edit_distance_separate":
    output_dir = output_dt_dir_cc
    print(f"{BLUE} Using {output_dir}{RESET} ")
else:
    output_dir = "media/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

csv_dir = "media/output/results.csv"


result_dir_base = ("media/output/result")
if ruleprefix == "N":
    result_dir_rp = os.path.join(result_dir_base, "/N")
elif ruleprefix == "W":
    result_dir_rp = os.path.join(result_dir_base, "/W")
elif ruleprefix == "QN":
    result_dir_rp = os.path.join(result_dir_base, "/QN")
elif ruleprefix == "QW":
    result_dir_rp = os.path.join(result_dir_base, "/QW")
if not os.path.exists(result_dir_rp):
    os.makedirs(result_dir_rp)

results_dir_s  = os.path.join(result_dir_rp, "/simple")
results_dir_cl = os.path.join(result_dir_rp, "/complex/lib")
results_dir_cc = os.path.join(result_dir_rp, "/complex/code")
results_dir_cw = os.path.join(result_dir_rp, "/complex/weighted")

if type_encoding == "simple":
    results_dir = results_dir_s
    print(f"{BLUE} Using {results_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "weighted_edit_distance":
    results_dir = results_dir_cw
    print(f"{BLUE} Using {results_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "edit_distance_lib":
    results_dir = results_dir_cl
    print(f"{BLUE} Using {results_dir}{RESET} ")
elif type_encoding == "complex" and selected_evaluation_edit_distance == "edit_distance_separate":
    results_dir = results_dir_cc
    print(f"{BLUE} Using {results_dir}{RESET} ")
else:
    results_dir = "media/output/result"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

postprocessing_folder = "media/postprocessing"

dataset_folder = "media/input"

# ========================================= checkers ===================================================================


existence_family = [ConstraintChecker.EXISTENCE,
                    ConstraintChecker.ABSENCE,
                    ConstraintChecker.INIT,
                    ConstraintChecker.EXACTLY]

choice_family = [ConstraintChecker.CHOICE,
                 ConstraintChecker.EXCLUSIVE_CHOICE]

positive_rel_family = [ConstraintChecker.RESPONDED_EXISTENCE,
                       ConstraintChecker.RESPONSE,
                       ConstraintChecker.ALTERNATE_RESPONSE,
                       ConstraintChecker.CHAIN_RESPONSE,
                       ConstraintChecker.PRECEDENCE,
                       ConstraintChecker.ALTERNATE_PRECEDENCE,
                       ConstraintChecker.CHAIN_PRECEDENCE
                       ]

negative_rel_family = [ConstraintChecker.NOT_RESPONDED_EXISTENCE,
                       ConstraintChecker.NOT_RESPONSE,
                       ConstraintChecker.NOT_CHAIN_RESPONSE,
                       ConstraintChecker.NOT_PRECEDENCE,
                       ConstraintChecker.NOT_CHAIN_PRECEDENCE]

checkers_cumulative = {"existence": existence_family}
checkers_cumulative["choice"] = checkers_cumulative["existence"] + choice_family
checkers_cumulative["positive relations"] = checkers_cumulative["choice"] + positive_rel_family
checkers_cumulative["negative relations"] = checkers_cumulative["positive relations"] + negative_rel_family

checkers = {"existence": existence_family,
            "choice": existence_family + choice_family,
            "positive relations": existence_family + positive_rel_family,
            "negative relations": existence_family + negative_rel_family,
            "all": checkers_cumulative['negative relations']}

constr_family_list = checkers.keys()

# ================ datasets ================


datasets_labels = {"bpic2011_f1": "bpic2011_1",
                   "bpic2011_f2": "bpic2011_2",
                   "bpic2011_f3": "bpic2011_3",
                   "bpic2011_f4": "bpic2011_4",
                   "bpic2012_accepted": "bpic2012_accepted",
                   "bpic2012_cancelled": "bpic2012_cancelled",
                   "bpic2012_declined": "bpic2012_rejected",
                   "bpic2015_1_f2": "bpic2015_1",
                   "bpic2015_2_f2": "bpic2015_2",
                   "bpic2015_3_f2": "bpic2015_3",
                   "bpic2015_4_f2": "bpic2015_4",
                   "bpic2015_5_f2": "bpic2015_5",
                   # "bpic2017_accepted": "bpic2017_accepted",
                   # "bpic2017_cancelled": "bpic2017_cancelled",
                   # "bpic2017_refused": "bpic2017_rejected",
                   "hospital_billing_2": "hospital_billing_1",
                   "hospital_billing_3": "hospital_billing_2",
                   "Production": "production",
                   "sepsis_cases_1": "sepsis_cases_1",
                   "sepsis_cases_2": "sepsis_cases_2",
                   "sepsis_cases_4": "sepsis_cases_3",
                   "traffic_fines_1": "traffic_fines",
                   }

# ================ hyperparameters ================


"""
hyperparameters = {'support_threshold': [support_threshold_dict['min']-0.2,
                                         support_threshold_dict['min']-0.1,
                                         support_threshold_dict['min'],
                                         support_threshold_dict['min']+0.1],
                   'class_weight': [None,
                                    'balanced'],
                   'min_samples_split': [2]
                   }
"""

dt_hyperparameters = {'criterion': ['entropy',
                                    'gini'],
                      'class_weight': ['balanced',
                                       None],
                      'max_depth': [4, 6, 8, 10,
                                    None],
                      'min_samples_split': [0.1, 2,
                                            0.2, 0.3],
                      'min_samples_leaf': [10,
                                           1,
                                           16]
                      }

num_feat_strategy = ['sqrt', 0.3, 0.5]

# num_feat_strategy = [0.5]

if quick:
    sat_threshold_list = [0.85]
else:
    sat_threshold_list = [0.55, 0.65, 0.75, 0.85]

    # sat_threshold_list = [0.35, 0.45, 0.55, 0.65]

if quick:
    weight_combination_list = [(0.4, 0.4, 0.2)]
else:
    weight_combination_list = [(0.2, 0.4, 0.4),
                               (0.6, 0.2, 0.2),
                               (0.4, 0.4, 0.2),
                               (0.4, 0.2, 0.4),
                               (0.8, 0.1, 0.1),
                               (0.4, 0.3, 0.3),
                               (0.1, 0.8, 0.1),
                               (0.1, 0.1, 0.8)
                               ]


# ================ checkers satisfaction ================


rules = {
    "vacuous_satisfaction": True,
    "activation": "",  # e.g. A.attr > 6
    "correlation": "",  # e.g. T.attr < 12
    "n": {
        ConstraintChecker.EXISTENCE: 1,
        ConstraintChecker.ABSENCE: 1,
        ConstraintChecker.EXACTLY: 1,
    }
}

# ================ plots ================


method_label = {'existence': r'$\mathcal{E}$',
                'choice': r'$\mathcal{\widehat{C}}$',
                'positive relations': r'$\mathcal{\widehat{PR}}$',
                'negative relations': r'$\mathcal{\widehat{NR}}$',
                'all': r'$\mathcal{A}$'
                }

method_marker = {'existence': 'x',
                 'choice': '1',
                 'positive relations': '.',
                 'negative relations': '',
                 'all': '+'
                 }

# method_color = {'existence': 'mediumpurple', 'choice': 'deepskyblue', 'positive relations': 'orange',
#                'negative relations': 'crimson', 'all': 'forestgreen'}

method_color = 'orange'

method_style = {'existence': 'solid',
                'choice': (0, (1, 1)),
                'positive relations': 'dashdot',
                'negative relations': (0, (5, 10)),
                'all': 'dashdot'
                }

# ======================================================================================================================
