import os
import pandas as pd


def calculate_metrics(input_directory, summary_file, weighted_summary_file):
    # Load existing summary data if files exist
    if os.path.exists(summary_file):
        summary_df = pd.read_csv(summary_file, sep=';')
    else:
        summary_df = pd.DataFrame(columns=['name_file', 'fscore(average)', 'recall(average)', 'precision(average)'])

    if os.path.exists(weighted_summary_file):
        weighted_summary_df = pd.read_csv(weighted_summary_file, sep=';')
    else:
        weighted_summary_df = pd.DataFrame(
            columns=['name_file', 'fscore(waverage)', 'recall(waverage)', 'precision(waverage)'])

    # Process each CSV file in the directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_directory, file_name)
            df = pd.read_csv(file_path)

            # Check if the required columns exist in the dataframe
            if not {'precision', 'recall', 'fscore', 'num_cases'}.issubset(df.columns):
                print(f"Skipping {file_name} as it does not contain the required columns.")
                continue

            # Calculate the average metrics
            avg_precision = df['precision'].mean()
            avg_recall = df['recall'].mean()
            avg_fscore = df['fscore'].mean()

            # Calculate the weighted average metrics
            total_cases = df['num_cases'].sum()
            w_avg_precision = (df['precision'] * df['num_cases']).sum() / total_cases
            w_avg_recall = (df['recall'] * df['num_cases']).sum() / total_cases
            w_avg_fscore = (df['fscore'] * df['num_cases']).sum() / total_cases

            # Create a DataFrame with the new data
            new_summary_data = pd.DataFrame([{
                'name_file': file_name,
                'fscore(average)': f'{avg_fscore:.3f}'.replace('.', ','),
                'recall(average)': f'{avg_recall:.3f}'.replace('.', ','),
                'precision(average)': f'{avg_precision:.3f}'.replace('.', ',')
            }])

            new_weighted_summary_data = pd.DataFrame([{
                'name_file': file_name,
                'fscore(waverage)': f'{w_avg_fscore:.3f}'.replace('.', ','),
                'recall(waverage)': f'{w_avg_recall:.3f}'.replace('.', ','),
                'precision(waverage)': f'{w_avg_precision:.3f}'.replace('.', ',')
            }])

            # Update or append the results in the summary DataFrames
            summary_df = pd.concat([summary_df[summary_df['name_file'] != file_name], new_summary_data],
                                   ignore_index=True)
            weighted_summary_df = pd.concat(
                [weighted_summary_df[weighted_summary_df['name_file'] != file_name], new_weighted_summary_data],
                ignore_index=True)

    # Save the updated DataFrames to CSV files
    summary_df.to_csv(summary_file, index=False, sep=';')
    weighted_summary_df.to_csv(weighted_summary_file, index=False, sep=';')

    print(f'{summary_file} and {weighted_summary_file} have been updated.')


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'result')
    output_directory = os.path.join(script_dir, '..', '..', 'media', 'output', 'postprocessing')

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    summary_file = os.path.join(output_directory, 'Summary.csv')
    weighted_summary_file = os.path.join(output_directory, 'Weighted_Summary.csv')

    calculate_metrics(input_directory, summary_file, weighted_summary_file)
