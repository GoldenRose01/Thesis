import os
import pandas as pd


def process_csv(file_path):
    df = pd.read_csv(file_path)

    precision_mean = round(df['precision'].mean() * 100, 2)
    recall_mean = round(df['recall'].mean() * 100, 2)
    fscore_mean = round(df['fscore'].mean() * 100, 2)

    total_cases = df['num_cases'].sum()
    precision_weighted = round((df['precision'] * df['num_cases']).sum() / total_cases * 100, 2)
    recall_weighted = round((df['recall'] * df['num_cases']).sum() / total_cases * 100, 2)
    fscore_weighted = round((df['fscore'] * df['num_cases']).sum() / total_cases * 100, 2)

    return precision_mean, recall_mean, fscore_mean, precision_weighted, recall_weighted, fscore_weighted


def get_upper_level_dir(path, stop_dirs):
    while os.path.basename(path) not in stop_dirs and os.path.basename(path):
        path = os.path.dirname(path)
    return os.path.basename(path)


def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        dataset_names = file.read().splitlines()
    return dataset_names


def find_dataset_name(file_name, dataset_names):
    for name in dataset_names:
        if name in file_name:
            return name
    return "Unknown"


def create_summary(input_dir, output_dir, dataset_names):
    summary_data = []

    for root, _, files in os.walk(input_dir):
        for file in files:
            if "evaluation" in file and file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                dataset_name = find_dataset_name(file, dataset_names)
                current_folder = os.path.basename(root)
                upper_folder = get_upper_level_dir(root, ['N', 'W', 'QN', 'QW'])

                precision_mean, recall_mean, fscore_mean, precision_weighted, recall_weighted, fscore_weighted = process_csv(
                    file_path)

                summary_data.append({
                    'dataset': dataset_name,
                    'current_folder': current_folder,
                    'upper_folder': upper_folder,
                    'precision_mean (%)': precision_mean,
                    'recall_mean (%)': recall_mean,
                    'fscore_mean (%)': fscore_mean,
                    'precision_weighted (%)': precision_weighted,
                    'recall_weighted (%)': recall_weighted,
                    'fscore_weighted (%)': fscore_weighted
                })

    summary_df = pd.DataFrame(summary_data)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, 'summary.csv')
    summary_df.to_csv(output_file, index=False)


dataset_names_file = 'datasetnames.txt'
dataset_names = load_dataset_names(dataset_names_file)

input_base_dir = 'media/output/result'
output_base_dir = 'media/postprocessing'

for root, dirs, _ in os.walk(input_base_dir):
    for dir in dirs:
        input_dir = os.path.join(root, dir)
        relative_path = os.path.relpath(input_dir, input_base_dir)
        output_dir = os.path.join(output_base_dir, relative_path)
        print(f"Processing directory: {input_dir}")
        create_summary(input_dir, output_dir, dataset_names)
