import pandas as pd
import os
import shutil
import re
from settings import excluded_attributes

def is_trace_attribute(column, df):
    if 'event_id' in df.columns:
        grouping_column = 'event_id'
    elif 'case_id' in df.columns:
        grouping_column = 'case_id'
    else:
        grouping_column = df.columns[0]
    is_constant_in_groups = df.groupby(grouping_column)[column].transform('nunique') == 1
    return is_constant_in_groups.all()

def is_resource_attribute(column, df):
    return df[column].dtype == object

def identify_trace_and_resource_attributes(df):
    trace_keywords = ['case', 'id', 'trace', 'process', 'age', 'Diagnose', 'Case ID']
    resource_keywords = ['resource', 'user', 'agent', 'group', 'role', 'operator', 'worker',
                         'member', 'participant', 'assignee', 'doctor', 'nurse', 'staff',
                         'officer', 'employee', 'Resource', 'User', 'Agent', 'Group', 'Role',]
    trace_attributes = []
    resource_attributes = []
    for col in df.columns:
        if col in excluded_attributes:
            continue
        if any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in trace_keywords):
            if is_trace_attribute(col, df):
                trace_attributes.append(col)
        elif any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in resource_keywords):
            resource_attributes.append(col)
        else:
            if is_resource_attribute(col, df):
                resource_attributes.append(col)
    return trace_attributes, resource_attributes

def find_csv_files(root_dir):
    csv_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(dirpath, file))
    return csv_files


root_directory = 'media/input'

csv_files = find_csv_files(root_directory)
trace_attributes = {}
resource_attributes = {}

for file_path in csv_files:
    if os.path.basename(file_path).startswith('xes_'):
        continue
    df = pd.read_csv(file_path, sep=';', low_memory=False)
    trace_attr, resource_attr = identify_trace_and_resource_attributes(df)
    # Get filename without extension
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    trace_attributes[file_name] = ';'.join(trace_attr)
    resource_attributes[file_name] = ';'.join(resource_attr)


# Write attributes to files
with open('Trace_att.txt', 'w') as trace_file:
    for file_name, attrs in trace_attributes.items():
        trace_file.write(f"{file_name}: {attrs}\n")

with open('Resource_att.txt', 'w') as resource_file:
    for file_name, attrs in resource_attributes.items():
        resource_file.write(f"{file_name}: {attrs}\n")

# Move the files to the target directory
target_directory = "src/machine_learning/encoding/Settings"
os.makedirs(target_directory, exist_ok=True)
shutil.move('Trace_att.txt', os.path.join(target_directory, 'Trace_att.txt'))
shutil.move('Resource_att.txt', os.path.join(target_directory, 'Resource_att.txt'))
