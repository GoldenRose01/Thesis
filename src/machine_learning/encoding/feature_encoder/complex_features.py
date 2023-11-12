from functools import reduce  # Importa il modulo functools per le funzioni riduzione
from pandas import DataFrame  # Importa la classe DataFrame dal modulo pandas
from src.machine_learning.encoding.constants import get_max_prefix_length, get_prefix_length, TaskGenerationType, \
    PrefixLengthStrategy  # Importa alcune funzioni e costanti necessarie
from src.machine_learning.label.common import \
    add_label_column  # Importa una funzione per aggiungere una colonna di etichette

ATTRIBUTE_CLASSIFIER = None  # Definisce una variabile globale ATTRIBUTE_CLASSIFIER

PREFIX_ = 'prefix_'  # Definisce un prefisso


def complex_features(log, prefix_length, padding, prefix_length_strategy, labeling_type, generation_type,
                              feature_list=None, target_event=None, trace_attributes=None, resource_attributes=None):
    """ Calcola le feature complesse da un log di eventi.

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

    # Calculate the maximum prefix length
    max_prefix_length = get_max_prefix_length(log, prefix_length, prefix_length_strategy, target_event)

    # Obtain columns for complex features and handle additional columns
    columns, additional_columns = _columns_complex(log, max_prefix_length, feature_list)
    columns_number = len(columns)
    encoded_data = []

    # Iterate through traces in the log
    for trace in log:
        trace_prefix_length = get_prefix_length(trace, prefix_length, prefix_length_strategy, target_event)

        # Ignore too short traces if padding is not required
        if len(trace) <= prefix_length - 1 and not padding:
            continue

        # Generate features for each trace based on the generation strategy
        if generation_type == TaskGenerationType.ALL_IN_ONE.value:
            for event_index in range(1, min(trace_prefix_length + 1, len(trace) + 1)):
                encoded_data.append(
                    _trace_to_row(trace, event_index, additional_columns, prefix_length_strategy, padding, columns,
                                  labeling_type))
        else:
            encoded_data.append(
                _trace_to_row(trace, trace_prefix_length, additional_columns, prefix_length_strategy, padding, columns,
                              labeling_type))

    # Create DataFrame from encoded data
    df = DataFrame(columns=columns, data=encoded_data)

    # Assuming the trace ID is available, add columns for trace and resource attributes
    if trace_attributes or resource_attributes:
        trace_id_column = log.columns[0]  # Adjust if the trace ID column is located differently
        df['trace_id'] = log[trace_id_column]

        if trace_attributes:
            df['trace_attributes'] = df['trace_id'].apply(lambda x: get_trace_attributes(x, trace_attributes))
        if resource_attributes:
            df['resource_attributes'] = df['trace_id'].apply(lambda x: get_resource_attributes(x, resource_attributes))

        # Combine trace ID and resource attributes into one column if both are present
        if trace_attributes and resource_attributes:
            df['combined_attributes'] = df.apply(
                lambda row: get_attributes(row['trace_id'], trace_attributes, resource_attributes), axis=1)

    return df


def _get_global_trace_attributes(log):
    # Ottiene tutti gli attributi di traccia nel log e restituisce la loro intersezione
    attributes = list(reduce(set.intersection, [set(trace._get_attributes().keys()) for trace in log]))
    trace_attributes = [attr for attr in attributes if attr not in ["concept:name", "time:timestamp", "label"]]
    return sorted(trace_attributes)


def _get_global_event_attributes(log):
    """Ottiene gli attributi dell'evento nel log che non sono il nome o il timestamp"""
    # Ottiene tutti gli eventi nel log e restituisce la loro intersezione
    attributes = list(reduce(set.intersection, [set(event._dict.keys()) for trace in log for event in trace]))
    event_attributes = [attr for attr in attributes if attr not in ["concept:name"]]
    return sorted(event_attributes)


def _compute_additional_columns(log) -> dict:
    # Calcola le colonne aggiuntive in base al log
    return {'trace_attributes': sorted([att for att in _get_global_trace_attributes(log) if att not in ["concept:name", "time:timestamp", "label"]]),
            'event_attributes': sorted([att for att in _get_global_event_attributes(log) if att not in ["concept:name"]])}

def _columns_complex(log, prefix_length: int, feature_list: list = None) -> tuple:
    # Calcola le colonne per le feature complesse
    additional_columns = _compute_additional_columns(log)
    columns = ['trace_id'] + additional_columns['trace_attributes']
    columns += [PREFIX_ + str(i) for i in range(1, prefix_length + 1)]
    for additional_column in additional_columns['event_attributes']:
        columns += [additional_column + "_" + str(i) for i in range(1, prefix_length + 1)]
    columns += ['label']
    if feature_list is not None:
        assert (list(feature_list) == columns)
    return columns, additional_columns



def _data_complex(trace, prefix_length: int, additional_columns: dict) -> list:
    """Crea una lista nella forma [1, value1, value2, 2, ...]

    Aggiunge i valori nelle colonne aggiuntive
    """
    data = [trace.attributes.get(att, 0) for att in additional_columns['trace_attributes']]
    for idx, event in enumerate(trace):
        if idx == prefix_length:
            break
        event_name = event["concept:name"]
        data.append(event_name)

        for att in additional_columns['event_attributes']:
            data.append(event.get(att, '0'))

    return data


def _trace_to_row(trace, prefix_length: int, additional_columns, prefix_length_strategy: str, padding, columns: list,
                  labeling_type) -> list:
    # Converte una traccia in una riga di dati per le feature complesse
    trace_row = [trace.attributes["concept:name"]]
    trace_row += _data_complex(trace, prefix_length, additional_columns)
    if padding or prefix_length_strategy == PrefixLengthStrategy.PERCENTAGE.value:
        trace_row += [0 for _ in range(len(trace_row), len(columns) - 1)]
    trace_row += [add_label_column(trace, labeling_type, prefix_length)]
    return trace_row
