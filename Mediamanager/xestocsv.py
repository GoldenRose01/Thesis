import xml.etree.ElementTree as ET
import pandas as pd
import os

def convert_xes_to_csv(xes_file_path, csv_file_path):
    context = ET.iterparse(xes_file_path, events=("start", "end"))
    context = iter(context)

    event, root = next(context)

    data = []
    current_trace_attributes = {}
    for event, elem in context:
        if elem.tag.endswith("trace") and event == "start":
            current_trace_attributes = {child.attrib['key']: child.attrib['value']
                                        for child in elem
                                        if child.tag.endswith(('string', 'date', 'int', 'float'))}
        elif elem.tag.endswith("event") and event == "end":
            event_data = {child.attrib['key']: child.attrib['value']
                          for child in elem
                          if child.tag.endswith(('string', 'date', 'int', 'float'))}
            event_data.update(current_trace_attributes)
            data.append(event_data)

        root.clear()

    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, index=False)

def convert_all_xes_in_directory(xes_directory, csv_directory):
    for file in os.listdir(xes_directory):
        if file.endswith('.xes'):
            xes_file_path = os.path.join(xes_directory, file)
            csv_file_name = 'xes_' + os.path.splitext(file)[0] + '.csv'
            csv_file_path = os.path.join(csv_directory, csv_file_name)
            convert_xes_to_csv(xes_file_path, csv_file_path)
            print(f"Converted {file} to {csv_file_name}")

# Percorsi delle cartelle
xes_directory = '../media/input/xes'
csv_directory = '../media/input/csvconverted'

# Converti tutti i file XES
convert_all_xes_in_directory(xes_directory, csv_directory)
