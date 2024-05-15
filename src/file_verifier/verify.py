import subprocess
import os
# ___Verifica se i file Resource_att.txt e Trace_att.txt esistono nella cartella desiderata___#
def attributes_verifier(directory):
    resource_filename = "Resource_att.txt"
    trace_filename = "Trace_att.txt"
    resource_att_path = directory + "/" + resource_filename
    trace_att_path = directory + "/" + trace_filename
    if not os.path.exists(resource_att_path) or not os.path.exists(trace_att_path):
        print("File non trovati. Esecuzione dello script script csvreader.")
        subprocess.run(["python", "Mediamanager/csvreader.py"])
    else:
        print("File trovati,inizio esperimento")

def remove_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            os.remove(os.path.join(directory, filename))
    print("File eliminati")

def remove_tmp_files(directory):
    for filename in os.listdir(directory):
        if not filename.endswith(".csv") or not filename.endswith(".pdf"):
            os.remove(os.path.join(directory, filename))
    print("File temporanei eliminati")

def structurize_results(directory):
    # Crea la struttura principale
    main_folders = ['simple', 'complex', 'declarative']
    complex_subfolders = ['edit_distance_lib', 'edit_distance_separate', 'weighted_edit_distance']

    for main_folder in main_folders:
        os.makedirs(os.path.join(directory, main_folder), exist_ok=True)

    for subfolder in complex_subfolders:
        os.makedirs(os.path.join(directory, 'complex', subfolder), exist_ok=True)

    # Funzione per determinare la destinazione in base al nome del file
    def determine_destination(parts):
        if len(parts) >= 4:
            encoding = parts[2]
            type_edit_distance = parts[3]

            if encoding == 'simple':
                return 'simple'
            elif encoding == 'complex':
                if 'edit_distance_lib' in type_edit_distance:
                    return os.path.join('complex', 'edit_distance_lib')
                elif 'edit_distance_separate' in type_edit_distance:
                    return os.path.join('complex', 'edit_distance_separate')
                elif 'weighted_edit_distance' in type_edit_distance:
                    return os.path.join('complex', 'weighted_edit_distance')
            elif encoding == 'declarative':
                return 'declarative'
        return None

    # Analizza e sposta i file nella giusta sottocartella
    for filename in os.listdir(directory):
        if filename.lower() == 'readme':
            continue  # Salta il file README

        if filename.endswith(('.pdf', '.csv', '.xlsx')):
            parts = filename.split('_')
            dest_folder = determine_destination(parts)

            if dest_folder:
                full_dest_path = os.path.join(directory, dest_folder, filename)
                source_path = os.path.join(directory, filename)

                # Se il file di destinazione esiste già, rimuoverlo
                if os.path.exists(full_dest_path):
                    os.remove(full_dest_path)

                # Sposta il file alla destinazione
                os.rename(source_path, full_dest_path)