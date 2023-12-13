import os
import glob
import xml.etree.ElementTree as ET

def extract_and_save_xes_data(xes_file_path, trace_attributes_dict, resource_dict):
    """Extracts and stores desired trace attributes and resources from a XES file."""
    context = ET.iterparse(xes_file_path, events=("start", "end"))
    context = iter(context)

    event, root = next(context)

    trace_attributes = {}
    resources = set()

    for event, elem in context:
        if elem.tag.endswith("trace") and event == "start":
            trace_attributes = {child.attrib['key']: child.attrib['value']
                                for child in elem
                                if child.tag.endswith(('string', 'date', 'int', 'float'))}
        elif elem.tag.endswith("event") and event == "end":
            resource = elem.find("./string[@key='org:resource']")
            if resource is not None:
                resources.add(resource.attrib['value'])
            root.clear()  # Free up memory

    trace_attributes_dict[xes_file_path] = trace_attributes
    resource_dict[xes_file_path] = resources

def process_all_xes_files(input_dir, trace_attributes_output_path, resource_output_path):
    # Ensure the output directories exist
    os.makedirs(os.path.dirname(trace_attributes_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(resource_output_path), exist_ok=True)

    trace_attributes_dict = {}
    resource_dict = {}

    # Process each XES file in the input directory
    for xes_file in glob.glob(os.path.join(input_dir, '*.xes')):
        extract_and_save_xes_data(xes_file, trace_attributes_dict, resource_dict)

    # Sort and save trace attributes to a text file
    with open(trace_attributes_output_path, 'w') as trace_attributes_file:
        for xes_file, attributes in sorted(trace_attributes_dict.items()):
            xes_file_name = os.path.splitext(os.path.basename(xes_file))[0]
            trace_attributes_str = '; '.join([f"{key}:{value}" for key, value in sorted(attributes.items())])
            trace_attributes_file.write(f"{xes_file_name}: {trace_attributes_str}\n")

    # Sort and save resources to a text file
    with open(resource_output_path, 'w') as resource_file:
        for xes_file, resources in sorted(resource_dict.items()):
            xes_file_name = os.path.splitext(os.path.basename(xes_file))[0]
            resources_str = '; '.join(sorted(resources))
            resource_file.write(f"{xes_file_name}: {resources_str}\n")

def main():
    input_dir = '../media/input/xes'
    trace_attributes_output_path = 'trace_attributes.txt'
    resource_output_path = 'resource.txt'

    process_all_xes_files(input_dir, trace_attributes_output_path, resource_output_path)

if __name__ == "__main__":
    main()
