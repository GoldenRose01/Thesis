import os
import shutil
import pandas as pd

"""
# FUnzione per convertire i file .xlsx in .csv quando non era stato introdotto il sistema exel
def convert_xlsx_to_csv(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.xlsx'):
                csv_filename = filename.replace('.xlsx', '.csv')
                csv_filepath = os.path.join(root, csv_filename)
                if not os.path.exists(csv_filepath):
                    xlsx_filepath = os.path.join(root, filename)
                    df = pd.read_excel(xlsx_filepath)
                    df.to_csv(csv_filepath, index=False)
                    print(f'Converted {filename} to {csv_filename}')
                else:
                    print(f'{csv_filename} already exists. Skipping conversion.')


# Esegui la funzione con la directory desiderata
convert_xlsx_to_csv('media/output/result')



# Funzione per spostare i file nelle cartelle corrette quando creati prima dell'autosorting
# Directory di input
input_directory = 'media/output/result/N' # sostituire a N le varie prefix W/QW e QN

# Mappatura delle stringhe alle cartelle di destinazione
mappings = {
    'simple': 'simple',
    'edit_distance_lib': 'complex/lib',
    'separate': 'complex/code',
    '0.0,0.0,1.0': 'complex/weighted/0% 0% 100%',
    '0%,0%,100%': 'complex/weighted/0% 0% 100%',
    '1.0,0.0,0.0': 'complex/weighted/100% 0% 0%',
    '100% 0% 0%': 'complex/weighted/100% 0% 0%',
    '0.0,1.0,0.0': 'complex/weighted/0% 100% 0%',
    '0% 100% 0%': 'complex/weighted/0% 100% 0%',
    '0.33,0.33,0.33': 'complex/weighted/33%',
    '33%,33%,33%': 'complex/weighted/33%',
    '0.25,0.5,0.25': 'complex/weighted/25% 50% 25%',
    '25%,50%,25%': 'complex/weighted/25% 50% 25%',
    '0.5,0.5,0.0': 'complex/weighted/50% 50% 0%',
    '50%,50%,0%': 'complex/weighted/50% 50% 0%',
    '0.0,0.5,0.5': 'complex/weighted/0% 50% 50%',
    '0%,50%,50%': 'complex/weighted/0% 50% 50%',
    '0.5,0.0,0.5': 'complex/weighted/50% 0% 50%',
    '50%,0%,50%': 'complex/weighted/50% 0% 50%'
}

# Creazione delle cartelle di destinazione se non esistono
for folder in set(mappings.values()):
    os.makedirs(os.path.join(input_directory, folder), exist_ok=True)

# Iterazione dei file nella directory di input e nelle sottodirectory
for root, dirs, files in os.walk(input_directory):
    for filename in files:
        file_path = os.path.join(root, filename)
        # Controllo se il nome del file contiene una delle stringhe specificate
        for key, folder in mappings.items():
            if key in filename:
                # Costruzione del percorso di destinazione
                dest_folder = os.path.join(input_directory, folder)
                dest_path = os.path.join(dest_folder, filename)
                # Spostamento del file
                shutil.move(file_path, dest_path)
                break

print("Organizzazione completata.")


# Rinomina i file nella directory principale e nelle sottodirectory se creati prima delle regole N
def process_files(root_directory):
    # Lista di file da eliminare perché non possono essere rinominati
    files_to_delete = []

    # Itera attraverso la directory principale e tutte le sottodirectory
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            old_filepath = os.path.join(dirpath, filename)

            # Controlla se il nome del file contiene "NNcomplex" e lo rinomina in "Ncomplex"
            if "NNcomplex" in filename:
                new_filename = filename.replace("NNcomplex", "Ncomplex")
            # Controlla se il nome del file contiene "complex" ma non "Ncomplex" e lo rinomina in "Ncomplex"
            elif "complex" in filename and "Ncomplex" not in filename:
                new_filename = filename.replace("complex", "Ncomplex")
            else:
                continue

            new_filepath = os.path.join(dirpath, new_filename)

            # Verifica se esiste già un file con il nuovo nome
            if os.path.exists(new_filepath):
                # Se esiste, aggiungi il file alla lista di quelli da eliminare
                files_to_delete.append(old_filepath)
            else:
                # Altrimenti, rinomina il file
                os.rename(old_filepath, new_filepath)

    # Elimina i file che non possono essere rinominati
    for filepath in files_to_delete:
        os.remove(filepath)
        print(f"Deleted file: {filepath}")


# Esegui la funzione sulla directory desiderata
process_files("media/output/result/N/complex")
"""