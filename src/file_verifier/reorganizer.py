import re
import os

# Function to load valid dataset names from the datasetnames.txt file
def load_valid_datasets(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to check if a dataset name is valid
def is_valid_dataset(dataset_name, valid_datasets):
    # Remove the trailing underscore if present
    if dataset_name.endswith('_'):
        dataset_name = dataset_name[:-1]
    return dataset_name in valid_datasets

# Load valid dataset names
valid_datasets = load_valid_datasets('datasetnames.txt')

# Define the pattern to match the file names
pattern = re.compile(r'([a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+)_[a-zA-Z]_(complex|simple)_(weighted_edit_distance|edit_distance|evaluation_weighted_edit_distance|evaluation_edit_distance|recommendations_weighted_edit_distance)([a-zA-Z0-9\.,]*)(?:\.csv|\.xlsx|\.pdf)?')

# Root directory containing the files
root_directory = 'path_to_your_project_root'  # Replace with your project's root directory path

# Function to check if a file should be ignored
def should_ignore(file_path):
    return 'media/output/dt' in file_path

# Process each file in the directory and its subdirectories
for root, _, files in os.walk(root_directory):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        if should_ignore(file_path):
            continue
        if file_name.endswith('.csv') or file_name.endswith('.xlsx') or file_name.endswith('.pdf'):
            match = pattern.match(file_name)
            if match:
                dataset_name = match.group(1)
                if is_valid_dataset(dataset_name, valid_datasets):
                    print(f"Match found: {match.groups()}")
                    print(f"Valid dataset: {dataset_name}")
                else:
                    print(f"Dataset {dataset_name} is not in the valid datasets list.")
            else:
                print(f"No pattern matched for file: {file_name}")
