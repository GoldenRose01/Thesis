import os
import pandas as pd
from settings import *

def calculate_weighted_average(df, column):
    total_weight = df['num_cases'].sum()
    if total_weight == 0:
        return 0
    return (df[column] * df['num_cases']).sum() / total_weight

def process_single_dataset(results_dir, dataset_name, rule_prefix, type_encoding, selected_evaluation_edit_distance,
                           namefile, wtrace_att=None, wactivities=None, wresource_att=None):
    file_path = namefile

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None

    df = pd.read_csv(file_path)

    required_columns = {'precision', 'recall', 'fscore', 'num_cases'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        print(f"File {namefile} does not contain the required columns: {missing_columns}")
        return None

    avg_fscore = df['fscore'].mean()
    avg_precision = df['precision'].mean()
    avg_recall = df['recall'].mean()

    weighted_avg_fscore = calculate_weighted_average(df, 'fscore')
    weighted_avg_precision = calculate_weighted_average(df, 'precision')
    weighted_avg_recall = calculate_weighted_average(df, 'recall')

    weighted_values = '/'
    if selected_evaluation_edit_distance == 'weighted_edit_distance' and all(
            v is not None for v in [wtrace_att, wactivities, wresource_att]):
        weighted_values = (f'{wtrace_att * 100:.0f}% {wactivities * 100:.0f}% {wresource_att * 100:.0f}%')

    return [
        dataset_name,  # dataset_name
        rule_prefix,  # letter
        type_encoding,  # complexity_type
        selected_evaluation_edit_distance,  # encoding_type
        weighted_values,  # weighted_values
        f'{avg_fscore:.3f}'.replace('.', ','),  # average fscore
        f'{avg_precision:.3f}'.replace('.', ','),  # average precision
        f'{avg_recall:.3f}'.replace('.', ','),  # average recall
        '|',  # blank column
        f'{weighted_avg_fscore:.3f}'.replace('.', ','),  # weighted average fscore
        f'{weighted_avg_precision:.3f}'.replace('.', ','),  # weighted average precision
        f'{weighted_avg_recall:.3f}'.replace('.', ',')  # weighted average recall
    ]

def append_to_summary(summary_file, data_row):
    if os.path.exists(summary_file):
        summary_df = pd.read_csv(summary_file, sep=';')
    else:
        summary_df = pd.DataFrame(columns=[
            'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
            'average_fscore', 'average_precision', 'average_recall', '', 'weighted_average_fscore',
            'weighted_average_precision', 'weighted_average_recall'
        ])

    # Convert the data row to a DataFrame
    new_row_df = pd.DataFrame([data_row], columns=summary_df.columns)

    # Concatenate the existing DataFrame with the new row
    summary_df = pd.concat([summary_df, new_row_df], ignore_index=True)

    # Sort the DataFrame by relevant columns
    summary_df = summary_df.sort_values(
        by=['dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values']
    )

    summary_df.to_csv(summary_file, index=False, sep=';')
    print(f'{summary_file} has been updated.')

def append_to_individual_summary(individual_summary_file, data_row):
    if os.path.exists(individual_summary_file):
        individual_summary_df = pd.read_csv(individual_summary_file, sep=';')
    else:
        individual_summary_df = pd.DataFrame(columns=[
            'dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values',
            'average_fscore', 'average_precision', 'average_recall', '', 'weighted_average_fscore',
            'weighted_average_precision', 'weighted_average_recall'
        ])

    new_row_df = pd.DataFrame([data_row], columns=individual_summary_df.columns)
    individual_summary_df = pd.concat([individual_summary_df, new_row_df], ignore_index=True)

    individual_summary_df = individual_summary_df.sort_values(
        by=['dataset_name', 'letter', 'complexity_type', 'encoding_type', 'weighted_values']
    )

    individual_summary_df.to_csv(individual_summary_file, index=False, sep=';')
    individual_summary_df.to_excel(individual_summary_file.replace('.csv', '.xlsx'), index=False)
    print(f'{individual_summary_file} has been updated.')

def process_and_update_summary(results_dir, postprocessing_folder, dataset_info):
    dataset_name = dataset_info['dataset_name']
    rule_prefix = dataset_info['rule_prefix']
    type_encoding = dataset_info['type_encoding']
    selected_evaluation_edit_distance = dataset_info['selected_evaluation_edit_distance']
    namefile = dataset_info['namefile']
    wtrace_att = dataset_info.get('wtrace_att')
    wactivities = dataset_info.get('wactivities')
    wresource_att = dataset_info.get('wresource_att')

    data_row = process_single_dataset(results_dir, dataset_name, rule_prefix, type_encoding,
                                      selected_evaluation_edit_distance, namefile, wtrace_att, wactivities,
                                      wresource_att)
    if data_row:
        summary_file = os.path.join(postprocessing_folder, 'Summary.csv')
        append_to_summary(summary_file, data_row)

        individual_summary_file = os.path.join(postprocessing_folder, f'{dataset_name}_summary.csv')
        append_to_individual_summary(individual_summary_file, data_row)
