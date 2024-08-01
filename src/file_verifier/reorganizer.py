import os
import shutil
import re

# Define the output directories
media_dir = 'media'
output_dirs = {
    'N': os.path.join(media_dir, 'output/Nresult'),
    'W': os.path.join(media_dir, 'output/Wresult'),
    'QN': os.path.join(media_dir, 'output/QNresult'),
    'QW': os.path.join(media_dir, 'output/QWresult')
}

# Read the dataset names from the datasetnames.txt file
with open('datasetnames.txt', 'r') as f:
    valid_datasets = set(f.read().splitlines())
    print("Open datasetnames.txt")

# Define the regular expressions for the file patterns
patterns = [
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>complex)_evaluation_(?P<selected_evaluation_edit_distance>weighted_edit_distance)(?P<settings>(?:0\.\d{1,2},){2}0\.\d{1,2})?\.csv$'),
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>simple|complex)_evaluation_(?P<selected_evaluation_edit_distance>edit_distance_lib|edit_distance_separate)?\.csv$'),

    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>complex)_(?P<selected_evaluation_edit_distance>weighted_edit_distance)(?P<settings>(?:0\.\d{1,2},){2}0\.\d{1,2})?_fscore\.pdf$'),
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>simple|complex)_(?P<selected_evaluation_edit_distance>edit_distance_lib|edit_distance_separate)?_fscore\.pdf$'),

    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>complex)_evaluation_(?P<selected_evaluation_edit_distance>weighted_edit_distance)(?P<settings>(?:0\.\d{1,2},){2}0\.\d{1,2})?\.xlsx$'),
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>simple|complex)_evaluation_(?P<selected_evaluation_edit_distance>edit_distance_lib|edit_distance_separate)?\.xlsx$'),

    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>complex)_reccomendations_(?P<selected_evaluation_edit_distance>weighted_edit_distance)(?P<settings>(?:0\.\d{1,2},){2}0\.\d{1,2})?\.xlsx$'),
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>simple|complex)_reccomendations_(?P<selected_evaluation_edit_distance>edit_distance_lib|edit_distance_separate)?\.xlsx$'),

    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>complex)_reccomendations_(?P<selected_evaluation_edit_distance>weighted_edit_distance)(?P<settings>(?:0\.\d{1,2},){2}0\.\d{1,2})?\.csv$'),
    re.compile(
        r'^(?P<dataset>.*?)(?P<ruleprefix>N|W|QN|QW)(?P<type_encoding>simple|complex)_reccomendations_(?P<selected_evaluation_edit_distance>edit_distance_lib|edit_distance_separate)?\.csv$'),
]


# Function to move files based on the regex match groups
def move_file(file_path, match):
    ruleprefix = match.group('ruleprefix')
    type_encoding = match.group('type_encoding')
    selected_evaluation_edit_distance = match.group('selected_evaluation_edit_distance')

    # Determine the destination directory based on the ruleprefix and type_encoding
    base_dir = output_dirs[ruleprefix]
    type_dir = os.path.join(base_dir, type_encoding)

    # Further divide complex type_encoding into subdirectories
    if type_encoding == 'complex':
        if selected_evaluation_edit_distance == 'edit_distance_lib':
            type_dir = os.path.join(type_dir, 'EDlib')
        elif selected_evaluation_edit_distance == 'edit_distance_separate':
            type_dir = os.path.join(type_dir, 'EDcode')
        elif selected_evaluation_edit_distance == 'weighted_edit_distance':
            type_dir = os.path.join(type_dir, 'wEd')

    # Create the destination directory if it doesn't exist
    os.makedirs(type_dir, exist_ok=True)

    # Move the file to the destination directory
    shutil.move(file_path, os.path.join(type_dir, os.path.basename(file_path)))
    print(f"{os.path.basename(file_path)} spostato in {type_dir}")


# Walk through the media directory and its subdirectories
for dirpath, _, filenames in os.walk(media_dir):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)

        # Check each pattern to see if the file matches
        for pattern in patterns:
            match = pattern.match(filename)
            if match:
                dataset = match.group('dataset')
                if dataset in valid_datasets:
                    move_file(file_path, match)
                break
