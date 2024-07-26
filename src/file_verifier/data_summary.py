import os
import pandas as pd
import re


def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        return {line.strip() for line in file}


def extract_weighted_values(file_name):
    match = re.search(r'weighted_edit_distance([\d.]+),([\d.]+),([\d.]+)', file_name)
    if match:
        return [value.rstrip('.') for value in match.groups()]
    return None


def parse_file_name(file_name, dataset_names):
    dataset_name = None
    for name in dataset_names:
        if name in file_name:
            dataset_name = name
            break
    if not dataset_name:
        return None

    letter = 'N'
    if '_W' in file_name:
        letter = 'W'

    complexity_type = 'simple' if 'simple' in file_name else 'complex'

    encoding_type = 'unknown'
    if 'edit_distance_lib_' in file_name:
        encoding_type = 'edit_distance_lib'
    elif 'edit_distance_separate_' in file_name:
        encoding_type = 'edit_distance_separate'
    elif 'weighted_edit_distance' in file_name:
        encoding_type = 'weighted_edit_distance'

    weighted_values = ''
    if encoding_type == 'weighted_edit_distance':
        weights = extract_weighted_values(file_name)
        if weights:
            weighted_values = (f'{float(weights[0]) * 100:.0f}% '
                               f'{float(weights[1]) * 100:.0f}% '
                               f'{float(weights[2]) * 100:.0f}%')

    return dataset_name, letter, complexity_type, encoding_type, weighted_values


def save_dataset_summary(dataset_name, summary_data, output_directory):
    summary_df = pd.DataFrame(summary_data, columns=[
        'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
        'prefix_length', 'precision', 'fscore'
    ])

    summary_file_csv = os.path.join(output_directory, f'{dataset_name}_summary.csv')
    summary_df.to_csv(summary_file_csv, index=False, sep=';')
    print(f'{summary_file_csv} has been created.')

    summary_file_excel = os.path.join(output_directory, f'{dataset_name}_summary.xlsx')
    summary_df.to_excel(summary_file_excel, index=False)
    print(f'{summary_file_excel} has been created.')


def calculate_metrics(input_directory, output_directory, dataset_names_file):
    dataset_names = load_dataset_names(dataset_names_file)

    summary_data_by_dataset = {}

    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            if file_name.endswith('.csv'):
                file_path = os.path.join(root, file_name)
                df = pd.read_csv(file_path)

                if not {'precision', 'fscore', 'prefix_length'}.issubset(df.columns):
                    print(f"Skipping {file_name} as it does not contain the required columns.")
                    continue

                parsed_values = parse_file_name(file_name, dataset_names)
                if not parsed_values:
                    print(f"Skipping {file_name} as the dataset name could not be determined.")
                    continue

                dataset_name = parsed_values[0]
                for _, row in df.iterrows():
                    summary_data_by_dataset.setdefault(dataset_name, []).append([
                        parsed_values[0],  # dataset_name
                        parsed_values[1],  # letter
                        parsed_values[2],  # complexity_type
                        parsed_values[3],  # encoding_type
                        parsed_values[4],  # weighted_values
                        row['prefix_length'],
                        row['precision'],
                        row['fscore']
                    ])

    for dataset_name, summary_data in summary_data_by_dataset.items():
        save_dataset_summary(dataset_name, summary_data, output_directory)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'result')
    output_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'postprocessing')

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    dataset_names_file = os.path.join(script_dir, '..', '..', 'datasetnames.txt')

    calculate_metrics(input_directory, output_directory, dataset_names_file)
