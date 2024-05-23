import subprocess
import os
import pandas as pd


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


def timeprinter(datasets_names,
                type_encoding,
                selected_evaluation_edit_distance,
                wtrace_att,
                wactivities,
                wresource_att,
                time_m_finale,
                file_path='Prospetto.xlsx'):
    # Definizione della leggenda base
    legend = ['Dataset_name', 'Simple', 'Complex edit_distance_lib', 'Complex edit_distance_separate',
              'Complex weighted_edit_distance(100,100,100)', 'Declarative']

    # Calcolo di a, b, c
    a = wtrace_att * 100
    b = wactivities * 100
    c = wresource_att * 100
    weighted_col_name = f"Complex weighted_edit_distance({a},{b},{c})"

    # Controllo se il file esiste
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
    else:
        df = pd.DataFrame(columns=legend)

    # Aggiungi la nuova colonna alla legenda se non esiste già
    if weighted_col_name not in df.columns:
        df[weighted_col_name] = ''

    # Costruzione della riga da aggiungere/aggiornare
    for dataset_name in datasets_names:
        new_row = {'Dataset_name': dataset_name, 'Simple': '', 'Complex edit_distance_lib': '',
                   'Complex edit_distance_separate': '', 'Complex weighted_edit_distance(100,100,100)': '',
                   'Declarative': ''}

        # Aggiunta valori basati sul tipo di encoding
        if type_encoding == 'simple':
            new_row['Simple'] = f"{time_m_finale}m"
        elif type_encoding == 'complex':
            if selected_evaluation_edit_distance == 'edit_distance_lib':
                new_row['Complex edit_distance_lib'] = f"{time_m_finale}m"
            elif selected_evaluation_edit_distance == 'edit_distance_separate':
                new_row['Complex edit_distance_separate'] = f"{time_m_finale}m"
            elif selected_evaluation_edit_distance == 'weighted_edit_distance':
                new_row[weighted_col_name] = f"{time_m_finale}m"

        # Controllo se il dataset esiste già nel DataFrame
        if dataset_name in df['Dataset_name'].values:
            # Aggiornamento della riga esistente
            for column in new_row:
                if new_row[column]:
                    df.loc[df['Dataset_name'] == dataset_name, column] = new_row[column]
        else:
            # Aggiunta di una nuova riga
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Salvataggio del DataFrame aggiornato nel file Excel
    df.to_excel(file_path, index=False)
