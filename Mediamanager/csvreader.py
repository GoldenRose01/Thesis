import pandas as pd
import os
import shutil

def identify_trace_and_resource_attributes(df):
    """
    Identifica gli attributi di traccia e risorsa in un DataFrame.
    :param df: DataFrame da analizzare
    :return: (attributo di traccia, attributo di risorsa)
    """
    # Identifica l'attributo di traccia (es. 'Case ID')
    trace_attribute = "Case ID" if "Case ID" in df.columns else None

    # Identifica l'attributo di risorsa (es. 'Resource')
    resource_attribute = "Resource" if "Resource" in df.columns else None

    # Cerca un attributo di risorsa alternativo se 'Resource' non è presente
    if not resource_attribute:
        for col in df.columns:
            if "resource" in col.lower() or "producer" in col.lower():
                resource_attribute = col
                break

    return trace_attribute, resource_attribute

# Percorso della cartella "media/input"
cartella_input = 'media/input'

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
    if trace_attr:
        trace_attributes[file_name] = trace_attr
    if resource_attr:
        resource_attributes[file_name] = resource_attr

# Scrivi le informazioni sugli attributi in file separati
with open('Trace_att.txt', 'w') as trace_file, open('Resource_att.txt', 'w') as resource_file:
    for file_name, attr in trace_attributes.items():
        trace_file.write(f"{file_name}: {attr}\n")
    for file_name, attr in resource_attributes.items():
        resource_file.write(f"{file_name}: {attr}\n")

# Definisci il percorso della directory target
target_directory = 'src/machine_learning/encoding'

# Crea la directory target se non esiste e sposta i file
os.makedirs(target_directory, exist_ok=True)
shutil.move('Trace_att.txt', os.path.join(target_directory, 'Trace_att.txt'))
shutil.move('Resource_att.txt', os.path.join(target_directory, 'Resource_att.txt'))
