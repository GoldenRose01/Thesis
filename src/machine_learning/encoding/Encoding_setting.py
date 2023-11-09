import os

# Percorsi dei file da cui leggere gli attributi
trace_attributes_path = 'src/machine_learning/encoding/Trace_att.txt'
resource_attributes_path = 'src/machine_learning/encoding/Resource_att.txt'

# Dizionario per contenere gli attributi del Trace ID
trace_attributes = {}

# Dizionario per contenere gli attributi delle risorse
resource_attributes = {}

# Leggi gli attributi Trace ID da Trace_att.txt
if os.path.exists(trace_attributes_path):
    with open(trace_attributes_path, 'r') as file:
        for line in file:
            # Assumi che il nome del file e l'attributo siano separati da ': '
            parts = line.strip().split(': ')
            if len(parts) == 2:
                file_name, attribute_value = parts
                trace_attributes[file_name] = attribute_value.split()  # Split by space to get multiple elements

# Leggi gli attributi delle risorse da Resource_att.txt
if os.path.exists(resource_attributes_path):
    with open(resource_attributes_path, 'r') as file:
        for line in file:
            # Assumi che il nome del file e l'attributo siano separati da ': '
            parts = line.strip().split(': ')
            if len(parts) == 2:
                file_name, attribute_value = parts
                resource_attributes[file_name] = attribute_value.split()  # Split by space to get multiple elements
