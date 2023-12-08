import pandas as pd
import os
import shutil
import re

def is_trace_attribute(column, df):
    """
    Determina se una colonna è un attributo di traccia.
    Verifica se i valori di una colonna sono costanti all'interno di ogni traccia.
    """
    # Trova una colonna che si possa usare per raggruppare le tracce (ad esempio, una colonna di eventi)
    # Qui stiamo supponendo che ci sia una colonna chiamata 'event_id' o simile
    if 'event_id' in df.columns:
        grouping_column = 'event_id'
    else:
        # Se non esiste una colonna 'event_id', scegli un'altra colonna appropriata
        # Potrebbe essere necessario adattare questo a seconda del dataset
        grouping_column = df.columns[0]

    # Raggruppa per la colonna di eventi/tracce e verifica la costanza della colonna in questione
    is_constant_in_groups = df.groupby(grouping_column)[column].transform('nunique') == 1
    return is_constant_in_groups.all()

def is_resource_attribute(column, df):
    """
    Determina se una colonna è un attributo di risorsa.
    Un attributo di risorsa spesso contiene stringhe e non ha una alta unicità come gli attributi di traccia.
    """
    return df[column].dtype == object

def identify_trace_and_resource_attributes(df):
    """
    Identifica gli attributi di traccia e risorsa in un DataFrame.
    :param df: DataFrame da analizzare
    :return: (lista di attributi di traccia, lista di attributi di risorsa)
    """
    trace_keywords = ['case', 'id', 'trace', 'process','age']
    resource_keywords = ['resource', 'user', 'agent', 'group', 'role', 'operator', 'worker',
                         'member', 'participant', 'assignee', 'doctor', 'nurse', 'staff',
                         'officer', 'employee']

    trace_attributes = []
    resource_attributes = []

    for col in df.columns:
        # Utilizza espressioni regolari per cercare parole chiave
        if any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in trace_keywords):
            if is_trace_attribute(col, df):
                trace_attributes.append(col)
        elif any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in resource_keywords):
            if is_resource_attribute(col, df):
                resource_attributes.append(col)

    # Rimuove i duplicati
    trace_attributes = list(set(trace_attributes))
    resource_attributes = list(set(resource_attributes))

    return trace_attributes, resource_attributes


def find_csv_files(root_dir):
    """
    Trova tutti i file CSV in una directory e nelle sue sottodirectory.
    :param root_dir: La directory radice da cui iniziare la ricerca
    :return: Una lista di percorsi di file CSV
    """
    csv_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(dirpath, file))
    return csv_files

# Percorso della cartella "media/input"
root_directory = '../media/input'

# Ottieni una lista di tutti i file CSV nella directory e nelle sue sottodirectory
csv_files = find_csv_files(root_directory)

# Dizionari per tracciare gli attributi di traccia e risorse per ciascun file
trace_attributes = {}
resource_attributes = {}

for file_path in csv_files:
    # Leggi il file CSV
    df = pd.read_csv(file_path, sep=';', low_memory=False)

    # Identifica gli attributi di traccia e risorsa
    trace_attr, resource_attr = identify_trace_and_resource_attributes(df)
    file_name = os.path.basename(file_path)
    trace_attributes[file_name] = ';'.join(trace_attr)
    resource_attributes[file_name] = ';'.join(resource_attr)

# Scrivi le informazioni sugli attributi in file separati
with open('Trace_att.txt', 'w') as trace_file, open('Resource_att.txt', 'w') as resource_file:
    for file_name, attrs in trace_attributes.items():
        trace_file.write(f"{file_name}: {attrs}\n")
    for file_name, attrs in resource_attributes.items():
        resource_file.write(f"{file_name}: {attrs}\n")

# Definisci il percorso della directory target
target_directory = '../src/machine_learning/encoding/Settings'

# Crea la directory target se non esiste e sposta i file
os.makedirs(target_directory, exist_ok=True)
shutil.move('Trace_att.txt', os.path.join(target_directory, 'Trace_att.txt'))
shutil.move('Resource_att.txt', os.path.join(target_directory, 'Resource_att.txt'))