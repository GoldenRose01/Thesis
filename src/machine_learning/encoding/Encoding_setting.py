import os
import re


def normalize_name(name):
    """
    Normalizza il nome rimuovendo i caratteri non alfanumerici e convertendo in minuscolo.
    """
    return re.sub(r'\W+', '', name).lower()


def read_attributes_from_file(file_path, dataset_name):
    """
    Legge gli attributi da un file e restituisce una lista con i valori per il dataset specificato.
    Ignora le differenze tra maiuscole e minuscole nel nome del dataset.

    :param file_path: Percorso del file da cui leggere gli attributi.
    :param dataset_name: Nome del dataset per cui filtrare gli attributi.
    :return: Lista degli attributi filtrati per il dataset specificato.
    """
    attributes = []
    normalized_dataset_name = normalize_name(dataset_name)

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    file_name, attribute_value = parts
                    normalized_file_name = normalize_name(file_name)
                    if normalized_file_name == normalized_dataset_name:
                        attributes = attribute_value.split(';')  # Split by ';' to get multiple elements
                        break  # Exit the loop once the dataset is found

    return attributes
