from pandas import DataFrame  # Importa la classe DataFrame dal modulo pandas
from src.machine_learning.label.common import \
    add_label_column  # Importa una funzione per aggiungere una colonna di etichette
from src.machine_learning.encoding.constants import TaskGenerationType, get_prefix_length, get_max_prefix_length, \
    PrefixLengthStrategy  # Importa alcune funzioni e costanti necessarie

ATTRIBUTE_CLASSIFIER = None  # Definisce una variabile globale ATTRIBUTE_CLASSIFIER come None
PREFIX_ = 'prefix_'  # Definisce un prefisso


def simple_features(log, prefix_length, padding, prefix_length_strategy: str, labeling_type, generation_type,
                    feature_list: list = None, target_event: str = None) -> DataFrame:
    # Questa funzione calcola le feature semplici basate sugli eventi nel log

    max_prefix_length = get_max_prefix_length(log, prefix_length, prefix_length_strategy, target_event)
    columns = _compute_columns(max_prefix_length)
    columns_number = len(columns)
    encoded_data = []

    # Itera attraverso le tracce nel log
    for trace in log:
        trace_prefix_length = get_prefix_length(trace, prefix_length, prefix_length_strategy, target_event)

        # Ignora le tracce troppo corte se non è richiesto il padding
        if len(trace) <= prefix_length - 1 and not padding:
            continue

        # Genera le feature semplici per ogni traccia in base alla strategia di generazione
        if generation_type == TaskGenerationType.ALL_IN_ONE.value:
            for event_index in range(1, min(trace_prefix_length + 1, len(trace) + 1)):
                encoded_data.append(
                    _trace_to_row(trace, event_index, columns_number, prefix_length_strategy, padding, labeling_type))
        else:
            encoded_data.append(
                _trace_to_row(trace, trace_prefix_length, columns_number, prefix_length_strategy, padding,
                              labeling_type))

    # Restituisce i dati encodati come DataFrame con le colonne appropriate
    return DataFrame(columns=columns, data=encoded_data)


def _trace_to_row(trace, prefix_length: int, columns_number: int, prefix_length_strategy: str, padding: bool = True,
                  labeling_type: str = None) -> list:
    """Converte una traccia in una riga di dati per le feature semplici"""
    trace_row = [trace.attributes['concept:name']]
    trace_row += _trace_prefixes(trace, prefix_length)

    # Aggiunge zero padding se richiesto o se la strategia di lunghezza è basata sulla percentuale
    if padding or prefix_length_strategy == PrefixLengthStrategy.PERCENTAGE.value:
        trace_row += [0 for _ in range(len(trace_row), columns_number - 1)]

    # Aggiunge l'etichetta
    trace_row += [add_label_column(trace, labeling_type, prefix_length)]

    return trace_row


def _trace_prefixes(trace, prefix_length: int) -> list:
    """Crea una lista di prefissi dell'evento in base alla lunghezza specificata"""
    prefixes = []
    counter = 0

    # Itera attraverso gli eventi nella traccia
    for idx, event in enumerate(trace):
        for attribute_key, attribute_value in event.items():
            if counter == prefix_length:
                break
            if (attribute_key == 'concept:name'):
                event_attribute = attribute_value
                counter = counter + 1
                prefixes.append(event_attribute)
    return prefixes


def contains_numbers_iterative(string):
    # Verifica se una stringa contiene numeri in modo iterativo
    for char in string:
        if char.isdigit():
            return True
    return False


def _compute_columns(prefix_length: int) -> list:
    """Calcola le colonne per le feature semplici"""
    return ["trace_id"] + [PREFIX_ + str(i + 1) for i in range(0, prefix_length)] + ['label']
