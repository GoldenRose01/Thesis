import pandas as pd
import os
import shutil
import re
from pm4py.objects.log.importer.xes import importer as xes_importer

def is_trace_attribute(column, df):
    if 'event_id' in df.columns:
        grouping_column = 'event_id'
    else:
        grouping_column = df.columns[0]
    is_constant_in_groups = df.groupby(grouping_column)[column].transform('nunique') == 1
    return is_constant_in_groups.all()

def is_resource_attribute(column, df):
    return df[column].dtype == object

def identify_trace_and_resource_attributes(df):
    trace_keywords = ['case', 'id', 'trace', 'process', 'age', 'Diagnose']
    resource_keywords = ['resource', 'user', 'agent', 'group', 'role', 'operator', 'worker',
                         'member', 'participant', 'assignee', 'doctor', 'nurse', 'staff',
                         'officer', 'employee']
    trace_attributes = []
    resource_attributes = []
    for col in df.columns:
        if any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in trace_keywords):
            if is_trace_attribute(col, df):
                trace_attributes.append(col)
        elif any(re.search(rf"\b{keyword}\b", col, re.IGNORECASE) for keyword in resource_keywords):
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

def find_xes_files(root_dir):
    xes_files = []
    xes_directory = os.path.join(root_dir, 'xes')
    for dirpath, dirnames, filenames in os.walk(xes_directory):
        for file in filenames:
            if file.endswith('.xes'):
                xes_files.append(os.path.join(dirpath, file))
    return xes_files

def process_xes_file(file_path):
    log = xes_importer.apply(file_path)
    trace_attributes = set()
    resource_attributes = set()
    for trace in log:
        for key in trace.attributes.keys():
            if 'trace' in key.lower():  # Identifica le trace attributes
                trace_attributes.add(key)
            else:
                resource_attributes.add(key)  # Altri attributi vengono considerati come resource attributes
        for event in trace:
            for key, value in event.items():
                if isinstance(value, str):  # Assumendo che gli attributi di risorsa siano stringhe
                    resource_attributes.add(key)
    return list(trace_attributes), list(resource_attributes)

root_directory = '../media/input'

csv_files = find_csv_files(root_directory)
trace_attributes = {}
resource_attributes = {}

for file_path in csv_files:
    if os.path.basename(file_path).startswith('xes_'):
        continue
    df = pd.read_csv(file_path, sep=';', low_memory=False)
    trace_attr, resource_attr = identify_trace_and_resource_attributes(df)
    file_name = os.path.splitext(os.path.basename(file_path))[0] + '.csv'  # Aggiunta dell'estensione .csv
    trace_attributes[file_name] = ' ; '.join(trace_attr)
    resource_attributes[file_name] = ' ; '.join(resource_attr)

xes_files = find_xes_files(root_directory)
for file_path in xes_files:
    trace_attr, resource_attr = process_xes_file(file_path)
    file_name = 'xes_' + os.path.splitext(os.path.basename(file_path))[0] + '.csv'  # Prefisso 'xes_' e aggiunta dell'estensione .csv
    trace_attributes[file_name] = ' ; '.join(trace_attr)
    resource_attributes[file_name] = ' ; '.join(resource_attr)

# Scrivi gli attributi di traccia e risorsa in file separati
with open('Trace_att.txt', 'w') as trace_file:
    for file_name, attrs in trace_attributes.items():
        trace_file.write(f"{file_name}: {attrs}\n")

with open('Resource_att.txt', 'w') as resource_file:
    for file_name, attrs in resource_attributes.items():
        resource_file.write(f"{file_name}: {attrs}\n")

# Resto del tuo codice rimane invariato

target_directory = '../src/machine_learning/encoding/Settings'
os.makedirs(target_directory, exist_ok=True)
shutil.move('Trace_att.txt', os.path.join(target_directory, 'Trace_att.txt'))
shutil.move('Resource_att.txt', os.path.join(target_directory, 'Resource_att.txt'))
