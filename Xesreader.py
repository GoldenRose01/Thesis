import xml.etree.ElementTree as ET
import os
import glob

def extract_and_save_xes_data(xes_file_path, resource_file_path, trace_attributes_file_path):
    """Extracts resource and trace attributes from a XES file and saves them into separate files."""
    context = ET.iterparse(xes_file_path, events=("start", "end"))
    context = iter(context)

    event, root = next(context)

    with open(resource_file_path, 'a') as resource_file, open(trace_attributes_file_path, 'a') as trace_attributes_file:
        for event, elem in context:
            if elem.tag.endswith("trace") and event == "start":
                # Extracting trace attributes
                trace_attributes = {child.attrib['key']: child.attrib['value']
                                    for child in elem
                                    if child.tag.endswith(('string', 'date', 'int', 'float'))}
                trace_attributes_file.write(str(trace_attributes) + "\n")

            elif elem.tag.endswith("event") and event == "end":
                # Extracting resource information from events
                resources = [child.attrib['value']
                             for child in elem
                             if child.tag.endswith('string') and child.attrib.get('key') == 'org:resource']
                for resource in resources:
                    resource_file.write(resource + "\n")

            root.clear()  # Free up memory

def process_all_xes_files(input_dir, resource_output_path, trace_attributes_output_path):
    # Ensure the output directories exist
    os.makedirs(os.path.dirname(resource_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(trace_attributes_output_path), exist_ok=True)

    # Process each XES file in the input directory
    for xes_file in glob.glob(os.path.join(input_dir, '*.xes')):
        extract_and_save_xes_data(xes_file, resource_output_path, trace_attributes_output_path)
        print(f"Processed: {xes_file}")

def main():
    input_dir = 'media/input/xes'
    resource_output_path = 'src/machine_learning/encoding/Resource_att.txt'
    trace_attributes_output_path = 'src/machine_learning/encoding/Trace_att.txt'

    process_all_xes_files(input_dir, resource_output_path, trace_attributes_output_path)

