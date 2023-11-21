import os

def read_attributes_from_file(file_path):
    """
    Legge gli attributi da un file e restituisce un dizionario con i valori.
    :param file_path: Percorso del file da cui leggere gli attributi.
    :return: Dizionario degli attributi.
    """
    attributes = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    file_name, attribute_value = parts
                    attributes[file_name] = attribute_value.split()  # Split by space to get multiple elements
    return attributes

# Percorsi dei file da cui leggere gli attributi
trace_attributes_path = 'src/machine_learning/encoding/Trace_att.txt'
resource_attributes_path = 'src/machine_learning/encoding/Resource_att.txt'

# Leggi gli attributi Trace ID e delle risorse
trace_attributes = read_attributes_from_file(trace_attributes_path)
resource_attributes = read_attributes_from_file(resource_attributes_path)

# Esempio di stampa per visualizzare i risultati
print("Trace Attributes:", trace_attributes)
print("Resource Attributes:", resource_attributes)
