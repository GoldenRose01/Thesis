import os
import pandas as pd
import re

def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        return {line.strip() for line in file}

def get_database_name(file_name, dataset_names):
    for name in dataset_names:
        if name in file_name:
            return name
    return "unknown"

def extract_weighted_values(file_name):
    match = re.search(r'weighted_edit_distance([\d.]+),([\d.]+),([\d.]+)', file_name)
    if match:
        return match.groups()
    return None

def calculate_metrics(input_directory, summary_file, dataset_names_file):
    # Load dataset names
    dataset_names = load_dataset_names(dataset_names_file)

    # Initialize summary data structures
    summary_data = {}

    # Process each CSV file in the directory and its subdirectories
    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            if file_name.endswith('.csv'):
                file_path = os.path.join(root, file_name)
                df = pd.read_csv(file_path)

                # Check if the required columns exist in the dataframe
                if not {'precision', 'recall', 'fscore', 'num_cases'}.issubset(df.columns):
                    print(f"Skipping {file_name} as it does not contain the required columns.")
                    continue

                # Calculate the average metrics
                avg_precision = df['precision'].mean()
                avg_recall = df['recall'].mean()
                avg_fscore = df['fscore'].mean()

                # Determine the database name
                database_name = get_database_name(file_name, dataset_names)

                if database_name not in summary_data:
                    summary_data[database_name] = {}

                # Determine the evaluation type and create appropriate columns
                if 'simple' in file_name:
                    summary_data[database_name].update({
                        'fscore(average)simple': f'{avg_fscore:.3f}'.replace('.', ','),
                        'recall(average)simple': f'{avg_recall:.3f}'.replace('.', ','),
                        'precision(average)simple': f'{avg_precision:.3f}'.replace('.', ',')
                    })
                elif 'separate' in file_name:
                    summary_data[database_name].update({
                        'fscore(average)distance_separate': f'{avg_fscore:.3f}'.replace('.', ','),
                        'recall(average)distance_separate': f'{avg_recall:.3f}'.replace('.', ','),
                        'precision(average)distance_separate': f'{avg_precision:.3f}'.replace('.', ',')
                    })
                elif 'weighted' in file_name:
                    weighted_values = extract_weighted_values(file_name)
                    if weighted_values:
                        weight_str = '_'.join(weighted_values)
                        summary_data[database_name].update({
                            f'fscore(average)weighted_edit_distance_{weight_str}': f'{avg_fscore:.3f}'.replace('.', ','),
                            f'recall(average)weighted_edit_distance_{weight_str}': f'{avg_recall:.3f}'.replace('.', ','),
                            f'precision(average)weighted_edit_distance_{weight_str}': f'{avg_precision:.3f}'.replace('.', ',')
                        })

    # Convert summary data to DataFrames
    summary_df = pd.DataFrame.from_dict(summary_data, orient='index').reset_index().rename(columns={'index': 'database_name'})

    # Save the updated DataFrame to a CSV file
    summary_df.to_csv(summary_file, index=False, sep=';')

    print(f'{summary_file} has been updated.')

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'result')
    output_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'postprocessing')

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    summary_file = os.path.join(output_directory, 'Summary.csv')
    dataset_names_file = os.path.join(script_dir, '..', '..', 'datasetnames.txt')

    calculate_metrics(input_directory, summary_file, dataset_names_file)
