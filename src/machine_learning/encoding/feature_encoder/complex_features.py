from functools import reduce
from pandas import DataFrame
from src.machine_learning.encoding.constants import get_max_prefix_length, get_prefix_length, PrefixLengthStrategy
from src.machine_learning.label.common import add_label_column
from src.machine_learning.encoding.Encoding_setting import trace_attributes, resource_attributes

ATTRIBUTE_CLASSIFIER = None  # Variabile globale, il suo utilizzo specifico non è chiaro dal contesto

PREFIX_ = 'prefix_'  # Prefisso utilizzato nelle colonne del DataFrame


def complex_features(log, prefix_length, padding, prefix_length_strategy, labeling_type, generation_type,
                     feature_list=None, target_event=None):
    """
    Calcola le feature complesse da un log di eventi.
    Args:
        log: Il log di eventi.
        prefix_length: La lunghezza del prefisso da utilizzare.
        padding: True se è necessario aggiungere zeri ai prefissi più corti, False altrimenti.
        prefix_length_strategy: La strategia per calcolare la lunghezza del prefisso.
        labeling_type: Il tipo di etichettatura da applicare.
        generation_type: Il tipo di generazione delle attività.
        feature_list: Una lista delle colonne delle feature da utilizzare.
        target_event: L'evento di destinazione da considerare.
        trace_attributes: Gli attributi delle tracce da includere.
        resource_attributes: Gli attributi delle risorse da includere.
    Returns:
        Un DataFrame contenente le feature complesse.
    """

    max_prefix_length = get_max_prefix_length(log, prefix_length, prefix_length_strategy, target_event)
    columns, additional_columns = _columns_complex(log, max_prefix_length, feature_list, trace_attributes, resource_attributes)
    encoded_data = []

    for trace_index, trace in enumerate(log):
        trace_prefix_length = get_prefix_length(trace, prefix_length, prefix_length_strategy, target_event)
        if len(trace) <= prefix_length - 1 and not padding:
            continue

        trace_encoded = _trace_to_row(trace, trace_prefix_length, additional_columns, prefix_length_strategy, padding,
                                      columns, labeling_type, trace_index)
        encoded_data.append(trace_encoded)

    df = DataFrame(columns=columns, data=encoded_data)
    return df


def _compute_additional_columns(log, trace_attributes, resource_attributes, prefix_length) -> dict:
    """
    Calcola le colonne aggiuntive in base agli attributi delle tracce e delle risorse.
    """

    excluded_attributes = ["concept:name", "time:timestamp", "label","Case ID"]

    trace_attrs = []
    for log, attributes_list in trace_attributes.items():
        trace_attrs = [
            attribute for attribute in trace_attributes.get(log,[])
            if attribute not in excluded_attributes
        ]

    resource_attrs = {}
    for key, attributes_list in resource_attributes.items():
        # Initialize the key with an empty list
        resource_attrs = []
        for attribute in attributes_list:
    resource_attrs = []
    for attribute in resource_attributes.get(log, []):
        if attribute not in excluded_attributes + trace_attrs:
            for i in range(prefix_length):
                resource_attrs.append(attribute + "_" + str(i + 1))

    return {'trace_attributes': trace_attrs, 'resource_attributes': resource_attrs}

def _columns_complex(log, prefix_length: int, feature_list: list, trace_attributes, resource_attributes) -> tuple:
    """
    Calcola le colonne per le feature complesse tenendo separate le feature delle tracce, eventi e risorse.
    """
    additional_columns = _compute_additional_columns(log, trace_attributes, resource_attributes, prefix_length)

    # Inizializzazione delle colonne
    columns = ['trace_id']

    # Aggiunta delle colonne degli attributi delle tracce
    for attrs in additional_columns['trace_attributes']:
        columns += [attrs]

    # Aggiunta delle colonne degli eventi
    columns += [PREFIX_ + str(i) for i in range(1, prefix_length + 1)]

    # Aggiunta delle colonne degli attributi delle risorse
    for attrs in additional_columns['resource_attributes']:
        columns += [attrs]

    columns += ['label']
    if feature_list is not None:
        assert (list(feature_list) == columns)
    return columns, additional_columns


def _trace_to_row(trace, prefix_length: int, additional_columns, prefix_length_strategy: str, padding, columns: list,
                  labeling_type, trace_index) -> list:
    """
    Converte una traccia in una riga di dati per le feature complesse.
    """
    trace_row = [trace.attributes["concept:name"]]

    # Aggiunta degli attributi delle tracce
    trace_row += [trace.attributes.get(att, 0) for att in additional_columns['trace_attributes']]

    # Aggiunta delle feature degli eventi
    for idx, event in enumerate(trace):
        if idx == prefix_length:
            break
        event_name = event["concept:name"]
        trace_row.append(event_name)

    # Padding se necessario
    if padding or prefix_length_strategy == PrefixLengthStrategy.PERCENTAGE.value:
        trace_row += [0 for _ in range(len(trace_row), len(columns) - 1 - len(additional_columns['resource_attributes']))]

    #Aggiunta delle feature delle risorse
    # Aggiunta delle feature delle risorse
    for idx, event in enumerate(trace):
        if idx == prefix_length:
            break
        if "org:group" in event:
            resource_name = event["org:group"]
        elif "group" in event:
            resource_name = event["group"]
        elif "Resource" in event:
            resource_name = event["Resource"]
        else:
            print("Unknown Event,need hardcode here")
        trace_row.append(resource_name)

    # Modifica per aggiungere il numero della riga alle risorse
   # resource_attributes_with_row_numbers = [f'{att}_{trace_index}' for att in additional_columns['resource_attributes']] #fai come eventi:riga 97 solo senza event name ma con risorsa
   # trace_row += [trace.attributes.get(att, 0) for att in resource_attributes_with_row_numbers]

    # Padding se necessario
    if padding or prefix_length_strategy == PrefixLengthStrategy.PERCENTAGE.value:
        trace_row += [0 for _ in
                      range(len(trace_row), len(columns) - 1)]

    # Aggiunta della colonna label
    trace_row += [add_label_column(trace, labeling_type, prefix_length)]

    return trace_row
