import os
import pandas as pd
import re

def load_dataset_names(file_path):
    with open(file_path, 'r') as file:
        return {line.strip() for line in file}

def extract_weighted_values(file_name):
    match = re.search(r'weighted_edit_distance([\d.]+),([\d.]+),([\d.]+)', file_name)
    if match:
        # Strip any trailing periods
        return [value.rstrip('.') for value in match.groups()]
    return None

def parse_file_name(file_name, dataset_names):
    # Extract dataset name
    dataset_name = None
    for name in dataset_names:
        if name in file_name:
            dataset_name = name
            break
    if not dataset_name:
        return None

    # Extract letter (N or W)
    letter = '/'
    if '_N' in file_name:
        letter = 'N'
    if '_W' in file_name:
        letter = 'W'
    elif '_QN' in file_name:
        letter = 'QN'
    elif '_QW' in file_name:
        letter = 'QW'

    # Extract complexity type (simple or complex)
    complexity_type = 'simple' if 'simple' in file_name else 'complex'

    # Extract encoding type
    encoding_type = 'edit_distance_lib_'
    if complexity_type == 'complex':
        if 'edit_distance_separate_' in file_name:
            encoding_type = 'edit_distance_separate_'
        elif 'weighted_edit_distance' in file_name:
            encoding_type = 'weighted_edit_distance'

    # Extract weighted values if applicable
    weighted_values = '/'
    if encoding_type == 'weighted_edit_distance':
        weights = extract_weighted_values(file_name)
        if weights:
            weighted_values = (f'{float(weights[0])*100:.0f}% '
                               f'{float(weights[1])*100:.0f}% '
                               f'{float(weights[2])*100:.0f}%')

    return dataset_name, letter, complexity_type, encoding_type, weighted_values

def calculate_weighted_average(df, column):
    total_weight = df['num_cases'].sum()
    if total_weight == 0:
        return 0
    return (df[column] * df['num_cases']).sum() / total_weight

def calculate_metrics(input_directory, summary_file, dataset_names_file):
    # Load dataset names
    dataset_names = load_dataset_names(dataset_names_file)

    # Initialize summary data structures
    summary_data = []

    # Process each CSV file in the directory and its subdirectories
    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            if file_name.endswith('.csv'):
                # Skip files containing 'recommendations' in their name
                if 'recommendations' in file_name:
                    print(f"Skipping {file_name} as it contains 'recommendations'.")
                    continue

                file_path = os.path.join(root, file_name)
                df = pd.read_csv(file_path)

                # Check if the required columns exist in the dataframe
                required_columns = {'precision', 'recall', 'fscore', 'num_cases'}
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    print(f"Skipping {file_name} as it does not contain the required columns: {missing_columns}")
                    continue

                # Calculate the average metrics
                avg_fscore = df['fscore'].mean()
                avg_precision = df['precision'].mean()

                # Calculate the weighted average metrics
                weighted_avg_fscore = calculate_weighted_average(df, 'fscore')
                weighted_avg_precision = calculate_weighted_average(df, 'precision')

                # Parse the file name
                parsed_values = parse_file_name(file_name, dataset_names)
                if not parsed_values:
                    print(f"Skipping {file_name} as the dataset name could not be determined.")
                    continue

                # Append the parsed values and metrics to the summary data
                summary_data.append([
                    parsed_values[0],  # dataset_name
                    parsed_values[1],  # letter
                    parsed_values[2],  # complexity_type
                    parsed_values[3],  # encoding_type
                    parsed_values[4],  # weighted_values
                    f'{avg_fscore:.3f}'.replace('.', ','),  # average fscore
                    f'{avg_precision:.3f}'.replace('.', ','),  # average precision
                    '|',  # blank column
                    f'{weighted_avg_fscore:.3f}'.replace('.', ','),  # weighted average fscore
                    f'{weighted_avg_precision:.3f}'.replace('.', ',')  # weighted average precision
                ])

    # Convert summary data to DataFrame
    summary_df = pd.DataFrame(summary_data, columns=[
        'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
        'average_fscore', 'average_precision', '', 'weighted_average_fscore', 'weighted_average_precision'
    ])

    # Sort the DataFrame by dataset_name and other relevant columns to maintain uniqueness
    summary_df = summary_df.sort_values(by=['dataset_name',
                                            'letter',
                                            'complexity_type',
                                            'encoding_type',
                                            'weighted_values'])

    # Save the updated DataFrame to a CSV file
    summary_df.to_csv(summary_file, index=False, sep=';')

    print(f'{summary_file} has been updated.')

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'result')
    output_directory = os.path.join(script_dir, '..', '..', 'media', 'postprocessing')

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    summary_file = os.path.join(output_directory, 'Summary.csv')
    dataset_names_file = os.path.join(script_dir, '..', '..', 'datasetnames.txt')

    calculate_metrics(input_directory, summary_file, dataset_names_file)
