import pdb  # Importa la libreria per il debugging

from src.enums import *  # Importa le enumerazioni da src.enums

# Calcola la media della soglia del label in base al tipo di labeling
def calc_mean_label_threshold(log, labeling):
    total = 0
    if labeling["type"] == LabelType.TRACE_DURATION:  # Se il tipo di labeling è TRACE_DURATION
        for trace in log:
            total += (trace[len(trace) - 1]["time:timestamp"] - trace[0]["time:timestamp"]).total_seconds()
            # Calcola la differenza di tempo tra l'inizio e la fine della traccia e sommala a total
    elif labeling["type"] == LabelType.TRACE_NUMERICAL_ATTRIBUTES:  # Se il tipo di labeling è TRACE_NUMERICAL_ATTRIBUTES
        trace_attribute = labeling["trace_attribute"]
        for trace in log:
            total += float(trace.attributes[trace_attribute])
            # Ottieni il valore dell'attributo specificato dalla traccia e sommalo a total come float
    mean_label_threshold = total / len(log)  # Calcola la media dividendo total per il numero di tracce nel log
    return mean_label_threshold  # Restituisce la media della soglia del label

# Genera il label per una traccia specifica in base al tipo di labeling
def generate_label(trace, labeling):
    if labeling["type"] == LabelType.DEFAULT:  # Se il tipo di labeling è DEFAULT
        if trace.attributes["label"] == "true":
            return TraceLabel.TRUE
        return TraceLabel.FALSE
        # Se l'attributo "label" della traccia è "true", restituisce TraceLabel.TRUE, altrimenti TraceLabel.FALSE
    elif labeling["type"] == LabelType.TRACE_CATEGORICAL_ATTRIBUTES:  # Se il tipo di labeling è TRACE_CATEGORICAL_ATTRIBUTES
        if trace[0][labeling["trace_lbl_attr"]] == labeling["trace_label"]:
            return TraceLabel.TRUE
        return TraceLabel.FALSE
        # Se il valore dell'attributo specificato dalla traccia all'inizio corrisponde al label specificato, restituisce TraceLabel.TRUE, altrimenti TraceLabel.FALSE
    elif labeling["type"] == LabelType.TRACE_DURATION:  # Se il tipo di labeling è TRACE_DURATION
        time_diff = (
                trace[len(trace) - 1]["time:timestamp"] - trace[0]["time:timestamp"]
        ).total_seconds()
        if time_diff < labeling["custom_threshold"]:
            return TraceLabel.TRUE
        return TraceLabel.FALSE
        # Calcola la differenza di tempo tra l'inizio e la fine della traccia e verifica se è inferiore alla soglia custom_threshold, in tal caso restituisce TraceLabel.TRUE, altrimenti TraceLabel.FALSE
    elif labeling["type"] == LabelType.TRACE_NUMERICAL_ATTRIBUTES:  # Se il tipo di labeling è TRACE_NUMERICAL_ATTRIBUTES
        trace_attribute = labeling["trace_attribute"]
        if float(trace.attributes[trace_attribute]) < labeling["custom_threshold"]:
            return TraceLabel.TRUE
        return TraceLabel.FALSE
        # Ottieni il valore dell'attributo specificato dalla traccia come float e verifica se è inferiore alla soglia custom_threshold, in tal caso restituisce TraceLabel.TRUE, altrimenti TraceLabel.FALSE

# Genera i label per tutte le tracce nel log in base al tipo di labeling
def generate_labels(log, labeling):
    result = []
    for trace in log:
        result.append(generate_label(trace, labeling).value)
    return result
    # Per ogni traccia nel log, chiama la funzione generate_label per generare il label e aggiungilo a result, quindi restituisci result
