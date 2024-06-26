from Colorlib.Colors import *
import pandas as pd
import subprocess
import settings
import main
import os


# ___Verifica se i file Resource_att.txt e Trace_att.txt esistono nella cartella desiderata___#
def attributes_verifier(directory):
    resource_filename = "Resource_att.txt"
    trace_filename = "Trace_att.txt"
    resource_att_path = directory + "/" + resource_filename
    trace_att_path = directory + "/" + trace_filename
    if not os.path.exists(resource_att_path) or not os.path.exists(trace_att_path):
        at_file_ver = f"{RED}File not found. Need to exe script csvreader.{RESET}"
        subprocess.run(["python", "src/file_verifier/csvreader.py"])
    else:
        at_file_ver = f"File found,no more extra things to do."
    print(f"{CREAM}{at_file_ver.center(main.infoconsole())}{RESET}\n\n")


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


def timeprinter(dataset_name,
                type_encoding,
                selected_evaluation_edit_distance,
                wtrace_att,
                wactivities,
                wresource_att,
                time_m_finale):
    file_path = 'Prospetto.csv'
    # Definizione della leggenda base
    legend = ['Dataset_name',
              'Simple',
              'Complex edit_distance_lib',
              'Complex edit_distance_separate',
              'Declarative']

    # Calcolo di a, b, c
    a = wtrace_att * 100
    b = wactivities * 100
    c = wresource_att * 100
    weighted_col_name = f"Complex weighted_edit_distance({a}%,{b}%,{c}%)"

    # Controllo se il file esiste
    if os.path.exists(file_path):
        encodings = ['utf-8', 'latin1', 'iso-8859-1']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, sep=',', encoding=encoding, on_bad_lines='skip')
                break
            except UnicodeDecodeError:
                print(f"Error reading {file_path} with encoding {encoding}. Trying next encoding")
            except pd.errors.ParserError as e:
                print(f"Parser error reading {file_path} with encoding {encoding}: {e}")
                return
        else:
            print(f"Failed to read {file_path} with available encodings.")
            return
    else:
        df = pd.DataFrame(columns=legend)

    # Ensure the 'Dataset_name' column exists
    if 'Dataset_name' not in df.columns:
        df['Dataset_name'] = ''

    # Aggiungi la nuova colonna alla legenda se non esiste già
    if weighted_col_name not in df.columns:
        df[weighted_col_name] = ''

    # Troncatura del tempo a due cifre decimali
    time_m_finale = f"{float(time_m_finale):.2f}"

    # Costruzione della riga da aggiungere/aggiornare
    new_row = {'Dataset_name': dataset_name, 'Simple': '', 'Complex edit_distance_lib': '',
               'Complex edit_distance_separate': '', weighted_col_name: '', 'Declarative': ''}

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

    # Determina il nome del dataset basato su settings.weighted_prefix_generation
    if settings.weighted_prefix_generation:
        dataset_row_name = f"{settings.ruleprefix}-{dataset_name}"
    else:
        dataset_row_name = dataset_name

    new_row['Dataset_name'] = dataset_row_name

    # Controllo se il dataset esiste già nel DataFrame
    if dataset_row_name in df['Dataset_name'].values:
        # Aggiornamento della riga esistente
        for column in new_row:
            if new_row[column]:
                df.loc[df['Dataset_name'] == dataset_row_name, column] = new_row[column]
    else:
        # Aggiunta di una nuova riga
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Salvataggio del DataFrame aggiornato nel file CSV
    df.to_csv(file_path, sep=',', index=False)
    if settings.selected_evaluation_edit_distance != "weighted_edit_distance":
        at_timeprint = f"File {file_path} successfully updated with"
        at_tp2 = f"{dataset_name} con {settings.selected_evaluation_edit_distance}"
    else:
        at_timeprint = f"File {file_path} successfully updated with"
        at_tp2 = f"{dataset_name} con {settings.selected_evaluation_edit_distance} al {wtrace_att},{wactivities},{wresource_att}."

    print(f"\n{AQUA_GREEN}{at_timeprint.center(main.infoconsole())}{RESET}")
    print(f"{AQUA_GREEN}{at_tp2.center(main.infoconsole())}{RESET}")
