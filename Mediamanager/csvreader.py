import pandas as pd
import os
import shutil

def identify_trace_and_resource_attributes(df):
    """
    Identifica gli attributi di traccia e risorsa in un DataFrame.
    :param df: DataFrame da analizzare
    :return: (lista di attributi di traccia, lista di attributi di risorsa)
    """
    # Identifica l'attributo di traccia (es. 'Case ID')
    trace_attributes = ['Case ID'] if 'Case ID' in df.columns else []

    # Identifica l'attributo di risorsa (es. 'Resource')
    resource_attributes = ['Resource'] if 'org:group' in df.columns else []

    # Cerca attributi di risorsa alternativi se 'Resource' non è presente
    if not resource_attributes:
        for col in df.columns:
            if "resource" in col.lower() or "producer" in col.lower():
                resource_attributes.append(col)

    return trace_attributes, resource_attributes

# Percorso della cartella "media/input"
cartella_input = 'media/input/processed_benchmark_event_logs'

# Ottieni una lista di tutti i file nella cartella "media/input"
elenco_file = [file for file in os.listdir(cartella_input) if file.endswith('.csv')]

# Dizionari per tracciare gli attributi di traccia e risorse per ciascun file
trace_attributes = {}
resource_attributes = {}

for file_name in elenco_file:
    # Leggi il file CSV
    df = pd.read_csv(os.path.join(cartella_input, file_name), sep=';', low_memory=False)

    # Identifica gli attributi di traccia e risorsa
    trace_attr, resource_attr = identify_trace_and_resource_attributes(df)
    trace_attributes[file_name] = ';'.join(trace_attr)
    resource_attributes[file_name] = ';'.join(resource_attr)

# Scrivi le informazioni sugli attributi in file separati
with open('Trace_att.txt', 'w') as trace_file, open('Resource_att.txt', 'w') as resource_file:
    for file_name, attrs in trace_attributes.items():
        trace_file.write(f"{file_name}: {attrs}\n")
    for file_name, attrs in resource_attributes.items():
        resource_file.write(f"{file_name}: {attrs}\n")

# Definisci il percorso della directory target
target_directory = 'src/machine_learning/encoding'

# Crea la directory target se non esiste e sposta i file
os.makedirs(target_directory, exist_ok=True)
shutil.move('Trace_att.txt', os.path.join(target_directory, 'Trace_att.txt'))
shutil.move('Resource_att.txt', os.path.join(target_directory, 'Resource_att.txt'))
