import pandas as pd
import os
import shutil

# Percorso della cartella "media/input"
cartella_input = 'media/input'

# Ottieni una lista di tutti i file nella cartella "media/input", escludendo "github_data.csv" e "Production.csv"
elenco_file = [file for file in os.listdir(cartella_input) if
               file.endswith('.csv') and file not in ['github_data.csv', 'Production.csv']]

# Dizionari per tracciare gli attributi di traccia e risorse per ciascun file
trace_attributes = {}
resource_attributes = {}

for file_name in elenco_file:
    # Leggi il file CSV e ignora gli avvisi DtypeWarning
    df = pd.read_csv(os.path.join(cartella_input, file_name), sep=';', low_memory=False)

    # Estrai i nomi delle colonne dal dataframe
    column_names = df.columns.tolist()

    # Crea un dizionario per tracciare i valori unici nelle colonne
    unique_values = {}
    for column_name in column_names:
        unique_values[column_name] = df[column_name].unique()

    # Scansiona le colonne per identificare attributi di traccia o risorsa
    for column_name in column_names:
        is_case_id = True
        for other_column in column_names:
            if column_name != other_column:
                # Controlla se ci sono valori unici diversi per lo stesso caso (Case ID)
                if df[df['Case ID'] == df[other_column]]['Case ID'].nunique() > 1:
                    is_case_id = False
                    break

        if is_case_id:
            # Se è un attributo Case ID, salva in trace_attributes
            trace_attributes[file_name] = column_name
        else:
            # Altrimenti, consideralo un attributo di risorsa
            resource_attributes[file_name] = column_name



# Scrivi le informazioni sugli attributi di traccia in Trace_att.txt
with open('Trace_att.txt', 'w') as trace_file:
    for file_name, trace_attribute in trace_attributes.items():
        trace_file.write(f"{file_name}: {trace_attribute}\n")

# Scrivi le informazioni sugli attributi di risorsa in Resource_att.txt
with open('Resource_att.txt', 'w') as resource_file:
    for file_name, resource_attribute in resource_attributes.items():
        resource_file.write(f"{file_name}: {resource_attribute}\n")

# Definisci il percorso della directory target
target_directory = 'src/machine_learning/encoding'

# Crea la directory target se non esiste
os.makedirs(target_directory, exist_ok=True)

# Sposta i file nella directory target
shutil.move('Trace_att.txt', f"{target_directory}/Trace_att.txt")
shutil.move('Resource_att.txt', f"{target_directory}/Resource_att.txt")
