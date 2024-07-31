import os
import pandas as pd
import itertools
import re

def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def calculate_weighted_average(df, column):
    total_weight = df['num_cases'].sum()
    if total_weight == 0:
        return 0
    return (df[column] * df['num_cases']).sum() / total_weight

def extract_weighted_values(file_name):
    match = re.search(r'weighted_edit_distance([\d.]+),([\d.]+),([\d.]+)', file_name)
    if match:
        return {
            'wtrace_att': float(match.group(1).rstrip('.')),
            'wactivities': float(match.group(2).rstrip('.')),
            'wresource_att': float(match.group(3).rstrip('.'))
        }
    return None

def generate_namefile(dataset, ruleprefix, type_encoding, selected_evaluation_edit_distance, settings=None):
    if selected_evaluation_edit_distance == 'weighted_edit_distance' and settings:
        return f"{dataset}_{ruleprefix}{type_encoding}_evaluation_{selected_evaluation_edit_distance}{settings['wtrace_att']},{settings['wactivities']},{settings['wresource_att']}.csv"
    else:
        return f"{dataset}_{ruleprefix}{type_encoding}_evaluation_{selected_evaluation_edit_distance}.csv"

def format_percentage(value):
    return f"{value * 100:.3f}%".rstrip('0').rstrip('.') if value < 1 else "100%"

def process_single_dataset(file_path, dataset_name, rule_prefix, type_encoding, selected_evaluation_edit_distance, settings=None):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None

    print(f"Reading file: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        print(f"File {file_path} is empty.")
        return None

    required_columns = {'precision', 'recall', 'fscore', 'num_cases'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        print(f"File {file_path} does not contain the required columns: {missing_columns}")
        return None

    avg_fscore = df['fscore'].mean()
    avg_precision = df['precision'].mean()
    avg_recall = df['recall'].mean()

    weighted_avg_fscore = calculate_weighted_average(df, 'fscore')
    weighted_avg_precision = calculate_weighted_average(df, 'precision')
    weighted_avg_recall = calculate_weighted_average(df, 'recall')

    # Convert values to percentages
    avg_fscore = format_percentage(avg_fscore)
    avg_precision = format_percentage(avg_precision)
    avg_recall = format_percentage(avg_recall)
    weighted_avg_fscore = format_percentage(weighted_avg_fscore)
    weighted_avg_precision = format_percentage(weighted_avg_precision)
    weighted_avg_recall = format_percentage(weighted_avg_recall)

    weighted_values = '/'
    if selected_evaluation_edit_distance == 'weighted_edit_distance' and settings:
        weighted_values = f'{settings["wtrace_att"] * 100:.0f}% {settings["wactivities"] * 100:.0f}% {settings["wresource_att"] * 100:.0f}%'

    if rule_prefix == '':
        rule_prefix = 'N'

    return [
        dataset_name,
        rule_prefix,
        type_encoding,
        selected_evaluation_edit_distance,
        weighted_values,
        avg_fscore,
        avg_precision,
        avg_recall,
        '|',
        weighted_avg_fscore,
        weighted_avg_precision,
        weighted_avg_recall
    ]

def append_to_summary(summary_file, data_row):
    if os.path.exists(summary_file):
        try:
            summary_df = pd.read_csv(summary_file, sep=';')
        except pd.errors.EmptyDataError:
            summary_df = pd.DataFrame(columns=[
                'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
                'average_fscore', 'average_precision', 'average_recall', '', 'weighted_average_fscore',
                'weighted_average_precision', 'weighted_average_recall'
            ])
    else:
        summary_df = pd.DataFrame(columns=[
            'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
            'average_fscore', 'average_precision', 'average_recall', '', 'weighted_average_fscore',
            'weighted_average_precision', 'weighted_average_recall'
        ])

    new_row = pd.DataFrame([data_row], columns=summary_df.columns)
    summary_df = pd.concat([summary_df, new_row], ignore_index=True)

    # Remove exact duplicate rows
    summary_df = summary_df.drop_duplicates()

    summary_df = summary_df.sort_values(
        by=['dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values'])

    summary_df.to_csv(summary_file, index=False, sep=';')

    print(f'{summary_file} has been updated.')

def compare_and_delete_if_needed(existing_file_path, new_data_row):
    existing_data = pd.read_csv(existing_file_path)

    existing_avg_fscore = existing_data['fscore'].mean()
    existing_avg_precision = existing_data['precision'].mean()
    existing_avg_recall = existing_data['recall'].mean()

    existing_weighted_avg_fscore = calculate_weighted_average(existing_data, 'fscore')
    existing_weighted_avg_precision = calculate_weighted_average(existing_data, 'precision')
    existing_weighted_avg_recall = calculate_weighted_average(existing_data, 'recall')

    # Compare average values and weighted values
    if (float(new_data_row[5].rstrip('%')) > existing_avg_fscore * 100 and
            float(new_data_row[6].rstrip('%')) > existing_avg_precision * 100 and
            float(new_data_row[7].rstrip('%')) > existing_avg_recall * 100 and
            float(new_data_row[10].rstrip('%')) > existing_weighted_avg_fscore * 100 and
            float(new_data_row[11].rstrip('%')) > existing_weighted_avg_precision * 100 and
            float(new_data_row[12].rstrip('%')) > existing_weighted_avg_recall * 100):
        os.remove(existing_file_path)
        print(f"Removed lower value file: {existing_file_path}")
        return True
    return False

def process_and_update_summary(results_dir, postprocessing_folder, dataset_names):
    rule_prefixes = ['N', 'W', 'QN', 'QW', '']  # Include an empty string to handle files without the rule prefix
    type_encodings = ['simple', 'complex']
    selected_evaluation_edit_distances = ['edit_distance_lib', 'edit_distance_separate', 'weighted_edit_distance']

    summary_file = os.path.join(postprocessing_folder, 'Summary.csv')

    for dataset in dataset_names:
        processed_files = {}
        for (rule_prefix, type_encoding, selected_evaluation_edit_distance) in itertools.product(rule_prefixes, type_encodings, selected_evaluation_edit_distances):
            for root, _, files in os.walk(results_dir):
                for file_name in files:
                    if file_name.endswith(".csv"):
                        file_path = os.path.join(root, file_name)
                        print(f"Found file: {file_path}")  # Debugging statement
                        normalized_name = file_name.replace(f"{dataset}_", f"{dataset}_N")
                        if selected_evaluation_edit_distance == 'weighted_edit_distance':
                            if file_name.startswith(f"{dataset}_{rule_prefix}{type_encoding}_evaluation_weighted_edit_distance"):
                                settings = extract_weighted_values(file_name)
                                data_row = process_single_dataset(file_path, dataset, rule_prefix, type_encoding, selected_evaluation_edit_distance, settings)
                                if data_row:
                                    unique_key = normalized_name
                                    if unique_key in processed_files:
                                        if compare_and_delete_if_needed(processed_files[unique_key], data_row):
                                            processed_files[unique_key] = file_path
                                        else:
                                            os.remove(file_path)
                                            print(f"Removed lower value file: {file_path}")
                                    else:
                                        processed_files[unique_key] = file_path
                                        append_to_summary(summary_file, data_row)
                        else:
                            namefile = generate_namefile(dataset, rule_prefix, type_encoding, selected_evaluation_edit_distance)
                            normalized_namefile = namefile.replace(f"{dataset}_", f"{dataset}_N")
                            if file_name == namefile or file_name == namefile.replace(f"{rule_prefix}_", ""):
                                data_row = process_single_dataset(file_path, dataset, rule_prefix, type_encoding, selected_evaluation_edit_distance)
                                if data_row:
                                    unique_key = normalized_name
                                    if unique_key in processed_files:
                                        if compare_and_delete_if_needed(processed_files[unique_key], data_row):
                                            processed_files[unique_key] = file_path
                                        else:
                                            os.remove(file_path)
                                            print(f"Removed lower value file: {file_path}")
                                    else:
                                        processed_files[unique_key] = file_path
                                        append_to_summary(summary_file, data_row)

                                        # Rename the file to include the rule prefix if needed
                                        if rule_prefix == '':
                                            new_file_path = os.path.join(root, normalized_namefile)
                                            os.rename(file_path, new_file_path)
                                            processed_files[unique_key] = new_file_path
                                            print(f"Renamed file: {file_path} to {new_file_path}")

    print(f'{summary_file} has been updated.')

if __name__ == "__main__":
    results_dir = os.path.join('media', 'output')
    postprocessing_folder = os.path.join('media', 'postprocessing')

    if not os.path.exists(postprocessing_folder):
        os.makedirs(postprocessing_folder)

    dataset_names_file = os.path.join('datasetnames.txt')
    dataset_names = load_dataset_names(dataset_names_file)

    process_and_update_summary(results_dir, postprocessing_folder, dataset_names)
