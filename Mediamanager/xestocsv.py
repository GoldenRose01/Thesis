import os
import xml.etree.ElementTree as ET
import pandas as pd

def parse_event_attributes(event, include_attrs=None, exclude_attrs=None):
    """
    Estrae gli attributi da un evento, gestendo diversi tipi di dati.
    """
    attributes = {}
    for element in event:
        key = element.get('key')
        if (include_attrs and key not in include_attrs) or (exclude_attrs and key in exclude_attrs):
            continue

        value = element.get('value')
        if element.tag.endswith('date'):
            value = pd.to_datetime(value).isoformat()
        attributes[key] = value
    return attributes

def process_trace(trace, ns, include_attrs=None, exclude_attrs=None):
    """
    Processa un singolo trace, estrae attributi di trace ed eventi.
    """
    trace_data = []
    trace_attributes = parse_event_attributes(trace, include_attrs, exclude_attrs)
    trace_id = trace_attributes.get('concept:name', 'Unknown')

    for event in trace.findall('xes:event', ns):
        event_data = parse_event_attributes(event, include_attrs, exclude_attrs)
        event_data['Case ID'] = trace_id
        event_data.update({k: v for k, v in trace_attributes.items() if k not in event_data})
        trace_data.append(event_data)

    return trace_data

def convert_xes_to_csv(xes_file_path, csv_file_path, case_id_col='Case ID', include_attrs=None, exclude_attrs=None):
    """
    Converte un file XES in un file CSV, migliorando la leggibilità e la modularità.
    """
    ns = {'xes': 'http://www.xes-standard.org/'}
    try:
        tree = ET.parse(xes_file_path)
    except ET.ParseError as e:
        print(f"Errore di parsing XML: {e}")
        return
    except Exception as e:
        print(f"Errore generico: {e}")
        return

    root = tree.getroot()
    data = [event for trace in root.findall('xes:trace', ns)
            for event in process_trace(trace, ns, include_attrs, exclude_attrs)]

    pd.DataFrame(data).to_csv(csv_file_path, index=False)

def convert_all_xes_in_directory(xes_directory, csv_directory):
    """
    Converte tutti i file XES in una cartella specificata in file CSV, nominando i file CSV con 'xes_'.
    """
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    for file in os.listdir(xes_directory):
        if file.endswith('.xes'):
            xes_file_path = os.path.join(xes_directory, file)
            csv_file_name = f"xes_{os.path.splitext(file)[0]}.csv"
            csv_file_path = os.path.join(csv_directory, csv_file_name)
            convert_xes_to_csv(xes_file_path, csv_file_path)
            print(f"Convertito: {file} -> {csv_file_name}")


# Esempio di utilizzo
xes_directory = '../media/input/xes'
csv_directory = '../media/input/csvconverted'
convert_all_xes_in_directory(xes_directory, csv_directory)
