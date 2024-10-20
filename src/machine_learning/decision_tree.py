import main
import graphviz
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from src.enums import *
from src.models import *
from Colorlib.Colors import *
from sklearn.metrics import f1_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from collections import Counter
from imblearn.over_sampling import ADASYN
from imblearn.combine import SMOTEENN
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from src.machine_learning.apriori import *
from src.machine_learning.encoding.encoding import *
from src.machine_learning.utils import *
from pm4py.objects.log import obj as log
from pm4py.objects.log.util.get_prefixes import get_log_with_log_prefixes
from src.machine_learning.encoding.feature_encoder.frequency_features import frequency_features
from src.machine_learning.encoding.feature_encoder.simple_features import simple_features
from src.machine_learning.encoding.feature_encoder.complex_features import complex_features
from src.machine_learning.encoding.Encoding_setting import read_attributes_from_file
from src.machine_learning.encoding.constants import EncodingType
from pandas import DataFrame
from src.machine_learning.encoding.data_encoder import *
from src.machine_learning.label.common import LabelTypes
import settings

# Definizione di un dizionario per associare il tipo di encoding alla funzione di encoding
TRACE_TO_DF = {
    EncodingType.SIMPLE.value: simple_features,
    EncodingType.FREQUENCY.value: frequency_features,
    EncodingType.COMPLEX.value: complex_features,
    # EncodingType.DECLARE.value : declare_features
}


# Funzione per trovare il miglior albero decisionale
def find_best_dt(dataset_name, data, support_threshold_dict, render_dt, dt_input_trainval,
                 resource_attributes, trace_attributes ):
    at_DT_par = f"DT params optimization"
    print(f"{PISTACHIO}{at_DT_par.center(main.infoconsole())}{RESET}")

    categories = [TraceLabel.FALSE.value, TraceLabel.TRUE.value]
    model_dict = {'dataset_name': dataset_name,
                  'parameters': (),
                  'f1_score_val': None,
                  'f1_score_train': None,
                  'f1_prefix_val': None,
                  'max_depth': 0,
                  'model': None}

    # Generazione degli eventi e delle coppie di eventi frequenti
    # (frequent_events_train, frequent_pairs_train) = generate_frequent_events_and_pairs(data,
    #                                                                                   support_threshold_dict['min'])

    # Generazione dell'input per l'albero decisionale
    if settings.train_prefix_log:
        prefix_log, trace_ids = get_log_with_log_prefixes(data)
        data = log.EventLog()
        for trace in prefix_log:
            if len(trace) > 2:
                data.append(trace)

    X_train = pd.DataFrame(dt_input_trainval.encoded_data, columns=dt_input_trainval.features)
    y_train = pd.Categorical(dt_input_trainval.labels, categories=categories)


    resource_attributes_for_log = []
    for attribute in resource_attributes:
        if attribute not in settings.excluded_attributes + trace_attributes:
            resource_attributes_for_log.append(attribute + "_")

    if settings.selected_evaluation_edit_distance == "weighted_edit_distance":
        if settings.wtrace_att == 0 and settings.wresource_att == 0 and settings.wactivities != 0:
            prefixcolumns = ["prefix_"]
        elif settings.wtrace_att == 0 and settings.wactivities == 0 and settings.wresource_att != 0:
            prefixcolumns = resource_attributes_for_log
        elif settings.wresource_att == 0 and settings.wactivities == 0 and settings.wtrace_att != 0:
            prefixcolumns = trace_attributes
        elif settings.wtrace_att == 0 and settings.wactivities != 0 and settings.wresource_att != 0:
            prefixcolumns = ["prefix_"] + resource_attributes_for_log
        elif settings.wresource_att == 0 and settings.wactivities != 0 and settings.wtrace_att != 0:
            prefixcolumns = trace_attributes + ["prefix_"]
        elif settings.wactivities == 0 and settings.wresource_att != 0 and settings.wtrace_att != 0:
            prefixcolumns = trace_attributes + resource_attributes_for_log
        else:
            prefixcolumns = trace_attributes + ["prefix_"] + resource_attributes_for_log
    else:
        prefixcolumns = trace_attributes + ["prefix_"] + resource_attributes_for_log

    X_train = X_train.astype(str)

    prefix_columns = []
    for attr in prefixcolumns:
        prefix_columns.extend([col for col in X_train.columns if col.startswith(attr)])

    one_hot_data = pd.get_dummies(X_train[prefix_columns], drop_first=True)
    new_feature_names = np.array(one_hot_data.columns)

    at_grid ="Grid search"
    print(f"{PEACHPUFF}{at_grid.center(main.infoconsole())}{RESET}")

    search = GridSearchCV(estimator=DecisionTreeClassifier(random_state=0), param_grid=settings.dt_hyperparameters,
                          scoring="f1", return_train_score=True, cv=5)
    search.fit(one_hot_data, y_train)
    model_dict['model'] = search.best_estimator_
    f1_score_train = round(100 * search.cv_results_['mean_train_score'][search.best_index_], 2)
    model_dict['f1_score_val'] = round(100 * search.best_score_, 2)
    model_dict['f1_score_train'] = f1_score_train
    model_dict['f1_prefix_val'] = -1
    model_dict['max_depth'] = search.best_estimator_.tree_.max_depth
    model_dict['parameters'] = tuple(search.best_params_.values())

    if render_dt:
        dot_data = tree.export_graphviz(search.best_estimator_, out_file=None, impurity=True,
                                        feature_names=new_feature_names, node_ids=True, filled=True)
        graph = graphviz.Source(dot_data, format="pdf")
        if settings.type_encoding != "complex":
            graph.render(os.path.join(settings.output_dir,
                                      f'DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}'))
            ptnamefile = (f'DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}')
        elif settings.selected_evaluation_edit_distance != "weighted_edit_distance":
            graph.render(os.path.join(settings.output_dir,
                                      f"DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}"
                                      f"_{settings.selected_evaluation_edit_distance}"))
            ptnamefile = (f"DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}"
                          f"_{settings.selected_evaluation_edit_distance}")
        else:
            graph.render(os.path.join(settings.output_dir,
                                      f"DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}_"
                                      f"{settings.selected_evaluation_edit_distance}{settings.wtrace_att}%,"
                                      f"{settings.wactivities}%,{settings.wresource_att}%"))
            ptnamefile = (f"DT_{dataset_name}_{settings.ruleprefix}{settings.type_encoding}_"
                          f"{settings.selected_evaluation_edit_distance}{settings.wtrace_att}%,"
                          f"{settings.wactivities}%,{settings.wresource_att}%")
        at_pdf = "PDF generated"
        print(f"{LILAC}{at_pdf.center(main.infoconsole())}{RESET}")
        print(f"{LILAC}{ptnamefile.center(main.infoconsole())}{RESET}")

    return model_dict, new_feature_names


# Funzione per calcolare lo score di un albero decisionale
def dt_score(dt_input):
    categories = [TraceLabel.FALSE.value, TraceLabel.TRUE.value]

    X = pd.DataFrame(dt_input.encoded_data, columns=dt_input.features)
    y = pd.Categorical(dt_input.labels, categories=categories)
    dtc = DecisionTreeClassifier(class_weight=None, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    dtc.fit(X_train, y_train)
    y_pred = dtc.predict(X_test)
    return f1_score(y_test, y_pred)


# Funzione per generare un albero decisionale basato su Boosting
def generate_boost_decision_tree(X_train, X_val, y_train, y_val):
    dtc = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=0).fit(X_train, y_train)
    dtc.fit(X_train, y_train)
    y_pred = dtc.predict(X_val)
    return dtc.estimators_[0, 0], f1_score(y_val, y_pred)


# Funzione per generare un albero decisionale
def generate_decision_tree(X_train, X_val, y_train, y_val, class_weight, min_samples_split, use_smote=False):
    count = Counter(y_train)
    pos_ratio = count[TraceLabel.TRUE.value] / count[TraceLabel.FALSE.value]

    if use_smote and pos_ratio <= 0.4:
        sm = SMOTE()
        sme = SMOTEENN()
        ada = ADASYN()
        X_train, y_train = sm.fit_resample(X_train, y_train)

    dtc = DecisionTreeClassifier(min_samples_split=min_samples_split, class_weight=class_weight, random_state=0)
    dtc.fit(X_train, y_train)
    y_pred = dtc.predict(X_val)
    y_pred_train = dtc.predict(X_train)
    return dtc, f1_score(y_val, y_pred), f1_score(y_train, y_pred_train)


# Funzione per generare i percorsi dell'albero decisionale
def generate_paths(dtc, dt_input_features, target_label):
    left = dtc.tree_.children_left
    right = dtc.tree_.children_right
    features = [dt_input_features[i] for i in dtc.tree_.feature]

    leaf_ids = np.argwhere(left == -1)[:, 0]
    if target_label == TraceLabel.TRUE:
        leaf_ids_positive = filter(
            lambda leaf_id: dtc.tree_.value[leaf_id][0][0] < dtc.tree_.value[leaf_id][0][1], leaf_ids)

    else:
        leaf_ids_positive = filter(
            lambda leaf_id: dtc.tree_.value[leaf_id][0][0] > dtc.tree_.value[leaf_id][0][1], leaf_ids)

    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = []
        if child in left:
            parent = np.where(left == child)[0].item()
            state = TraceState.VIOLATED
        else:
            parent = np.where(right == child)[0].item()
            state = TraceState.SATISFIED

        lineage.append((features[parent], state, parent))

        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)

    paths = []
    for leaf_id in leaf_ids_positive:
        rules = []
        for node in recurse(left, right, leaf_id):
            rules.append(node)
        if target_label == TraceLabel.TRUE:
            num_samples = {
                "node_samples": dtc.tree_.n_node_samples[leaf_id],
                "negative": dtc.tree_.value[leaf_id][0][0],
                "positive": dtc.tree_.value[leaf_id][0][1],
                "total": dtc.tree_.value[leaf_id][0][0] + dtc.tree_.value[leaf_id][0][1]
            }
        else:
            num_samples = {
                "node_samples": dtc.tree_.n_node_samples[leaf_id],
                "negative": dtc.tree_.value[leaf_id][0][1],
                "positive": dtc.tree_.value[leaf_id][0][0],
                "total": dtc.tree_.value[leaf_id][0][0] + dtc.tree_.value[leaf_id][0][1]
            }
        path = PathModel(
            impurity=dtc.tree_.impurity[leaf_id],
            num_samples=num_samples,
            rules=rules
        )
        paths.append(path)

    return paths


def process_log_and_model(log, dt_params, support_threshold_dict, dataset_name, render_dt,
                          resource_attributes, trace_attributes):
    # Encoding complesso
    complex_data, index = complex_features(log, {})
    X = complex_data.drop(columns=['label'])  # Rimuove la colonna della label
    y = complex_data['label']  # Assumi che la label sia presente in complex_data

    # Dividi i dati in training e validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)

    # Ottimizzazione dell'albero decisionale
    model_dict, feature_names = find_best_dt(dataset_name, complex_data, support_threshold_dict, render_dt,
                                             (X_train, y_train), resource_attributes, trace_attributes)

    # Calcolo dello score F1
    f1 = dt_score((X_val, y_val, feature_names))

    # Generazione dei percorsi dell'albero decisionale
    paths = generate_paths(model_dict['model'], feature_names, LabelTypes.TRUE.value)

    return f1, paths
