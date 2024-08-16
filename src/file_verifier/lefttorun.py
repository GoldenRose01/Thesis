import os
import csv


def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        dataset_names = file.read().splitlines()
    return dataset_names


def check_missing_datasets(directory, dataset_names, encoding, edit_d=None, percentages=None):
    missing_datasets = []
    for dataset_name in dataset_names:
        found = False
        for filename in os.listdir(directory):
            if filename.endswith(".csv") and dataset_name in filename:
                found = True
                break
        if not found:
            missing_datasets.append(dataset_name)

    if missing_datasets:
        return {
            "encoding": encoding,
            "dataset_names": missing_datasets,
            "edit_d": edit_d,
            "percentages": percentages
        }
    return None


def process_directory(root_directory, dataset_names):
    missing_files = []

    for dirpath, dirnames, filenames in os.walk(root_directory):
        for dirname in dirnames:
            current_dir = os.path.join(dirpath, dirname)
            if "simple" in current_dir:
                result = check_missing_datasets(current_dir, dataset_names, "simple")
                if result:
                    missing_files.append(result)
            elif "complex/lib" in current_dir:
                result = check_missing_datasets(current_dir, dataset_names, "complex", "lib")
                if result:
                    missing_files.append(result)
            elif "complex/code" in current_dir:
                result = check_missing_datasets(current_dir, dataset_names, "complex", "code")
                if result:
                    missing_files.append(result)
            elif "complex/weighted" in current_dir:
                percentages = dirname.replace("complex/weighted/", "")
                if percentages == "33%":
                    percentages = "33% 33% 33%"
                result = check_missing_datasets(current_dir, dataset_names, "complex", "weighted", percentages)
                if result:
                    missing_files.append(result)

    return missing_files


def save_to_csv(missing_files, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["encoding", "dataset_names", "edit_d", "percentages"])

        for entry in missing_files:
            encoding = entry.get("encoding")
            dataset_names = " ".join(entry.get("dataset_names", []))
            edit_d = entry.get("edit_d", "null")
            percentages = entry.get("percentages", "null")
            writer.writerow([encoding, dataset_names, edit_d, percentages])


# Percorsi dei file e delle directory
root_directory = "media/output/result/N"
dataset_names_file = "datasetnames.txt"
output_file = "left.csv"

# Carica i nomi dei dataset
dataset_names = load_dataset_names(dataset_names_file)

# Processa la directory e trova i dataset mancanti
missing_files = process_directory(root_directory, dataset_names)

# Salva i risultati in un file CSV
save_to_csv(missing_files, output_file)

print("Process completed. Results saved to", output_file)
