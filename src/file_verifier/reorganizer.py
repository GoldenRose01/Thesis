import os
import re

# Funzione per caricare i nomi dei dataset validi dal file datasetnames.txt
def load_valid_datasets(file_path):
    try:
        with open(file_path, 'r') as file:
            datasets = [line.strip() for line in file.readlines()]
        print(f"Caricati {len(datasets)} dataset validi.")
        return datasets
    except Exception as e:
        print(f"Errore durante il caricamento dei dataset validi: {e}")
        return []

# Funzione per normalizzare i nomi dei dataset
def normalize_dataset_name(dataset_name):
    dataset_name = dataset_name.lower().replace("dt_", "").replace("_", "").replace(" ", "")
    print(f"Nome dataset normalizzato: {dataset_name}")
    return dataset_name

# Funzione per controllare se un nome di dataset è valido
def is_valid_dataset(dataset_name, valid_datasets):
    dataset_name = normalize_dataset_name(dataset_name)
    normalized_valid_datasets = [normalize_dataset_name(ds) for ds in valid_datasets]
    is_valid = dataset_name in normalized_valid_datasets
    print(f"Dataset '{dataset_name}' valido: {is_valid}")
    return is_valid

# Funzione per controllare se un file deve essere ignorato
def should_ignore(file_path):
    ignore = 'postprocessing' in file_path
    print(f"Ignorare file '{file_path}': {ignore}")
    return ignore

# Funzione per rinominare e spostare un singolo file
def process_file(file_path, valid_datasets, root_directory):
    pattern = re.compile(
        r'(DT_)?([a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*)_?(\w*)_(complex|simple)_(weighted_edit_distance|edit_distance|evaluation_weighted_edit_distance|evaluation_edit_distance|recommendations_weighted_edit_distance|evaluation_edit_distance_lib)?([a-zA-Z0-9\.,]*)(?:\.csv|\.xlsx|\.pdf)?')

    file_name = os.path.basename(file_path)
    if should_ignore(file_path):
        return
    print(f"Elaborazione del file: {file_name}")
    if file_name.endswith('.csv') or file_name.endswith('.xlsx') or file_name.endswith('.pdf'):
        match = pattern.match(file_name)
        if match:
            dt_prefix = match.group(1) or ""
            dataset_name = match.group(2)
            ruleprefix = match.group(3) or "N"
            type_encoding = match.group(4)
            selected_evaluation_edit_distance = match.group(5) or ""
            percentages = match.group(6) or ""

            print(f"Pattern trovato per il file: {file_name}")
            print(
                f"dt_prefix: {dt_prefix}, dataset_name: {dataset_name}, ruleprefix: {ruleprefix}, type_encoding: {type_encoding}, selected_evaluation_edit_distance: {selected_evaluation_edit_distance}, percentages: {percentages}")

            if is_valid_dataset(dataset_name, valid_datasets):
                print(f"Dataset valido trovato: {dataset_name}")
                # Normalizza i valori percentuali
                new_percentages = ""
                if 'weighted_edit_distance' in selected_evaluation_edit_distance:
                    percentage_values = re.findall(r'\d+\.\d+', percentages)
                    percentage_values = [f"{int(float(p) * 100)}%" for p in percentage_values]
                    new_percentages = ','.join(percentage_values)
                    new_file_name = file_name.replace(percentages, new_percentages)
                    print(f"Valori percentuali normalizzati: {new_percentages}")
                else:
                    new_file_name = file_name

                # Ricostruisci il nuovo nome del file
                new_file_name = f"{dt_prefix}{dataset_name}_{ruleprefix}_{type_encoding}"
                if selected_evaluation_edit_distance:
                    new_file_name += f"_{selected_evaluation_edit_distance}"
                if new_percentages:
                    new_file_name += new_percentages

                # Aggiungi l'estensione del file
                new_file_name += os.path.splitext(file_name)[1]

                # Definisci il percorso di destinazione
                if dt_prefix:
                    new_path = os.path.join(root_directory, 'DT', ruleprefix, type_encoding,
                                            selected_evaluation_edit_distance)
                else:
                    new_path = os.path.join(root_directory, 'result', ruleprefix, type_encoding,
                                            selected_evaluation_edit_distance)

                if 'weighted_edit_distance' in selected_evaluation_edit_distance:
                    new_path = os.path.join(new_path, new_percentages)

                print(f"Percorso di destinazione: {new_path}")
                os.makedirs(new_path, exist_ok=True)
                new_file_path = os.path.join(new_path, new_file_name)
                os.rename(file_path, new_file_path)
                print(f"File {file_name} rinominato e spostato in {new_file_path}")
            else:
                print(f"Dataset {dataset_name} non è nella lista dei dataset validi.")
        else:
            print(f"Nessun pattern trovato per il file: {file_name}")

# Funzione di lancio per analizzare tutta la cartella e le sottocartelle
def process_directory(directory_path, valid_datasets):
    print(f"Analisi della directory: {directory_path}")
    for root, _, files in os.walk(directory_path):
        print(f"Esplorazione della cartella: {root}")
        for file_name in files:
            print(f"Trovato file: {file_name}")
            file_path = os.path.join(root, file_name)
            process_file(file_path, valid_datasets, directory_path)

if __name__ == "__main__":
    # Percorso del file datasetnames.txt
    datasetnames_file_path = 'datasetnames.txt'

    # Carica i nomi dei dataset validi
    valid_datasets = load_valid_datasets(datasetnames_file_path)
    print("Dataset validi caricati:", valid_datasets)

    # Directory radice contenente i file estratti
    root_directory = '/data/output'

    # Processa tutta la directory
    process_directory(root_directory, valid_datasets)
