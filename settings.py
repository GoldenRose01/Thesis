import os
from src.enums.ConstraintChecker import ConstraintChecker
def read_options_from_dat(filepath):
    options = {}
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                if value.lower() in ['true', 'false']:
                    options[key] = value.lower() == 'true'
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

#========================================paths===========================================================
options_filepath = 'Option.dat'
datasets_names_filepath = 'Datasets_names.dat'
encoding_path = 'Encoding.dat'
#========================================encoding_selection==============================================
def read_type_encoding(filepath):
    with open(filepath, 'r') as file:
        type_encoding = file.readline().strip()
        print("Encoding type: ", type_encoding)
    return type_encoding

#type_encoding = read_type_encoding(encoding_path)
type_encoding = 'complex'
# simple, frequency, complex
#========================================datasets_names===================================================
datasets_names = read_datasets_from_dat(datasets_names_filepath)

# datasets_names = ["bpic2011_f1","bpic2011_f2","bpic2011_f3","bpic2011_f4","bpic2012_accepted","bpic2012_cancelled","bpic2012_declined","bpic2015_3_f2","bpic2015_4_f2","bpic2015_5_f2","bpic2017_accepted","bpic2017_cancelled","bpic2017_refused","hospital_billing_2","hospital_billing_3","Production","sepsis_cases_1","sepsis_cases_2","sepsis_cases_4","traffic_fines_1"]

# datasets_names = ["Production"]

# datasets_names = ["hospital_billing_3"]

# datasets_names = ["bpic2012_cancelled", "bpic2012_declined"]

# datasets_names = ["bpic2011_f4","bpic2012_accepted","sepsis_cases_1","sepsis_cases_2","sepsis_cases_4"]

# datasets_names = ["traffic_fines_1"]

#datasets_names = ["sepsis_cases_4"]

#datasets_names = ["bpic15_1","bpic15_2","bpic15_3","bpic15_4","bpic15_5"]
"""
sat_threshold = 0.75
top_K_paths = 6
reranking = False
sat_type = 'count_occurrences'
fitness_type = 'mean'
cumulative_res = False
optimize_dt = True
print_dt = True
compute_gain = False
smooth_factor = 1
num_classes = 2
train_prefix_log = False
one_hot_encoding = False
use_score = True
compute_baseline = False
Print_edit_distance = False
excluded_attributes = ["concept:name", "time:timestamp", "label", "Case ID"]
"""
#==================================================read_options_from_dat==================================================
options = read_options_from_dat(options_filepath)
# ================================================= thresholds ===============================================================================
support_threshold_dict= {'min': 0.05, 'max': 1.75}
sat_threshold = options['sat_threshold']
top_K_paths = options['top_K_paths']
reranking = options['reranking']
sat_type = options['sat_type']
fitness_type = options['fitness_type']
cumulative_res = options['cumulative_res']
optimize_dt = options['optimize_dt']
print_dt = options['print_dt']
compute_gain = options['compute_gain']
smooth_factor = options['smooth_factor']
num_classes = options['num_classes']
train_prefix_log = options['train_prefix_log']
one_hot_encoding = options['one_hot_encoding']
use_score = options['use_score']
compute_baseline = options['compute_baseline']
Print_edit_distance = options['Print_edit_distance']
excluded_attributes = options['excluded_attributes']

# ================ weights ================
wtrace_att=0.25
wsimple_encoding=0.5
wresource_att=0.25
#weights of the three components of the encoding

# ================ folders ================
output_dir = "media/output"
results_dir = os.path.join(output_dir, "result")
#dataset_folder = "media/input/processed_benchmark_event_logs"
dataset_folder = "media/input"

# ================ checkers ================
existence_family = [ConstraintChecker.EXISTENCE, ConstraintChecker.ABSENCE, ConstraintChecker.INIT,
                    ConstraintChecker.EXACTLY]

choice_family = [ConstraintChecker.CHOICE, ConstraintChecker.EXCLUSIVE_CHOICE]

positive_rel_family = [ConstraintChecker.RESPONDED_EXISTENCE, ConstraintChecker.RESPONSE,
                       ConstraintChecker.ALTERNATE_RESPONSE, ConstraintChecker.CHAIN_RESPONSE,
                       ConstraintChecker.PRECEDENCE, ConstraintChecker.ALTERNATE_PRECEDENCE,
                       ConstraintChecker.CHAIN_PRECEDENCE]

negative_rel_family = [ConstraintChecker.NOT_RESPONDED_EXISTENCE, ConstraintChecker.NOT_RESPONSE,
                       ConstraintChecker.NOT_CHAIN_RESPONSE, ConstraintChecker.NOT_PRECEDENCE,
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
                   "bpic2017_accepted": "bpic2017_accepted",
                   "bpic2017_cancelled": "bpic2017_cancelled",
                   "bpic2017_refused": "bpic2017_rejected",
                   "hospital_billing_2": "hospital_billing_1",
                   "hospital_billing_3": "hospital_billing_2",
                   "Production": "production",
                   "sepsis_cases_1": "sepsis_cases_1",
                   "sepsis_cases_2": "sepsis_cases_2",
                   "sepsis_cases_4": "sepsis_cases_3",
                   "traffic_fines_1": "traffic_fines",
                   "xes_BPIC15_1": "xes_BPIC15_1",
                   "xes_BPIC15_2": "xes_BPIC15_2",
                   "xes_BPIC15_3": "xes_BPIC15_3",
                   "xes_BPIC15_4": "xes_BPIC15_4",
                   "xes_BPIC15_5": "xes_BPIC15_5",
                   "xes_BPI_Challenge_2012": "xes_BPI_Challenge_2012",
                   "xes_Hospital Billing - Event Log": "xes_Hospital_Billing",
                   "xes_Road_Traffic_Fine_Management_Process": "xes_Road_Traffic_Fine",
                   "xes_Sepsis Cases - Event Log": "xes_Sepsis_cases"
                   }


# ================ hyperparameters ================
"""
hyperparameters = {'support_threshold': [support_threshold_dict['min']-0.2, support_threshold_dict['min']-0.1,
                                         support_threshold_dict['min'],
                                         support_threshold_dict['min']+0.1],
                   'class_weight': [None, 'balanced'],
                   'min_samples_split': [2]}
"""
dt_hyperparameters = {'criterion': ['entropy', 'gini'],
                      'class_weight': ['balanced', None],
                      'max_depth': [4, 6, 8, 10, None],
                      'min_samples_split': [0.1, 2, 0.2, 0.3],
                      'min_samples_leaf': [10, 1, 16]}

num_feat_strategy = ['sqrt', 0.3, 0.5]
# num_feat_strategy = [0.5]
# sat_threshold_list = [0.55, 0.65, 0.75, 0.85]
sat_threshold_list = [0.35, 0.45, 0.55, 0.65]
# sat_threshold_list = [0.85]
weight_combination_list = [(0.2, 0.4, 0.4), (0.6, 0.2, 0.2), (0.4, 0.4, 0.2), (0.4, 0.2, 0.4), (0.8, 0.1, 0.1),
                           (0.4, 0.3, 0.3), (0.1, 0.8, 0.1), (0.1, 0.1, 0.8)]
# weight_combination_list = [(0.4, 0.4, 0.2)]

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
method_label = {'existence': r'$\mathcal{E}$', 'choice': r'$\mathcal{\widehat{C}}$',
                'positive relations': r'$\mathcal{\widehat{PR}}$', 'negative relations': r'$\mathcal{\widehat{NR}}$',
                'all': r'$\mathcal{A}$'}
method_marker = {'existence': 'x', 'choice': '1', 'positive relations': '.', 'negative relations': '', 'all': '+'}
# method_color = {'existence': 'mediumpurple', 'choice': 'deepskyblue', 'positive relations': 'orange',
#                'negative relations': 'crimson', 'all': 'forestgreen'}
method_color = 'orange'
method_style = {'existence': 'solid', 'choice': (0, (1, 1)), 'positive relations': 'dashdot',
                'negative relations': (0, (5, 10)), 'all': 'dashdot'}
