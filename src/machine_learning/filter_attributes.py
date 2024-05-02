from settings import excluded_attributes
from src.machine_learning.encoding.Encoding_setting import trace_attributes, resource_attributes
import numpy as np

def get_attributes_by_dataset(dataset_name):
    """
    Retrieves attributes relevant to the given dataset name.

    Args:
        dataset_name: Name of the dataset (without the .csv extension).

    Returns:
        tuple: A tuple of lists containing trace attributes and resource attributes for the specified dataset.
    """
    # Ensure the input is stripped of potential whitespace and converted to lowercase for consistency
    dataset_name = dataset_name.strip().lower()

    # Filter resource attributes based on dataset
    resource_dataset_attributes = resource_attributes.get(dataset_name, [])
    trace_dataset_attributes = trace_attributes.get(dataset_name, [])

    # Optional: Exclude certain attributes if necessary
    if excluded_attributes:
        resource_dataset_attributes = [attr for attr in resource_dataset_attributes if attr not in excluded_attributes]
        trace_dataset_attributes = [attr for attr in trace_dataset_attributes if attr not in excluded_attributes]

    return trace_dataset_attributes, resource_dataset_attributes

def array_index(n,trace_att_d,resource_att_d):
    # Calcolo della lunghezza dei blocchi
    ta_len = len(trace_att_d)
    p_len = ta_len + n
    # Lunghezza iniziale del blocco risorsa
    start_r_len = p_len
    # Inizializzazione del dizionario degli indici
    list_of_index = {
        'blocco_trace_att': list(range(0, ta_len)),
        'blocco_prefix': list(range(ta_len, p_len))
    }

    # Generazione degli indici per i blocchi risorse
    for i in range(len(resource_att_d)):
        # Calcola l'indice di inizio e fine per ciascun blocco risorsa
        end_r_len = start_r_len + n
        block_name = f'blocco_risorsa_{i + 1}'
        list_of_index[block_name] = list(range(start_r_len, end_r_len))
        # Aggiorna l'inizio del prossimo blocco risorsa
        start_r_len = end_r_len

    return list_of_index

def remove_n_prefixes(list_of_index, m):
    # Aggiorna il blocco dei prefissi
    if isinstance(list_of_index['blocco_prefix'], list) and len(list_of_index['blocco_prefix']) > m:
        list_of_index['blocco_prefix'] = list_of_index['blocco_prefix'][m:]
    else:
        list_of_index['blocco_prefix'] = []
    # Aggiorna il blocco delle risorse
    keys_to_update = [key for key in list_of_index if key.startswith('blocco_risorsa_')]
    for key in keys_to_update:
        if isinstance(list_of_index[key], list) and len(list_of_index[key]) > m:
            list_of_index[key] = list_of_index[key][m:]
        else:
            list_of_index[key] = []

    return list_of_index

def rm_vect_element(hyp, list_of_index, m, resource_att_d):
    if not isinstance(hyp, np.ndarray):
        hyp = np.array(hyp)

    # Determina gli indici da rimuovere
    indici_da_rimuovere = []
    if m <= len(list_of_index.get('blocco_prefix', [])):
        indici_da_rimuovere.extend(list_of_index['blocco_prefix'][:m])
    else:
        indici_da_rimuovere.extend(list_of_index.get('blocco_prefix', []))

    # Itera su ciascun blocco risorsa dinamico
    for i in range(len(resource_att_d)):
        block_name = f'blocco_risorsa_{i + 1}'
        if block_name in list_of_index:
            risorsa_indici = list_of_index[block_name]
            if m <= len(risorsa_indici):
                indici_da_rimuovere.extend(risorsa_indici[:m])
            else:
                indici_da_rimuovere.extend(risorsa_indici)

    # Filtra gli indici che sono entro i limiti di hyp
    indici_da_rimuovere = [i for i in indici_da_rimuovere if i < len(hyp)]

    # Crea una maschera booleana per mantenere gli indici validi
    mask = np.ones(len(hyp), dtype=bool)
    mask[indici_da_rimuovere] = False

    # Applica la maschera
    nuovo_hyp = hyp[mask]

    # Effettua check
    new_len = len(nuovo_hyp)
    expected_len = len(hyp) - m * (1 + len(resource_att_d))
    if new_len != expected_len:
        raise ValueError(f"Errore nella rimozione degli elementi: {len(hyp)} - {m} * (1 + {len(resource_att_d)}) = {new_len} invece di {expected_len}")

    return nuovo_hyp

def update_hyp_indices(hyp, list_of_index, indices, m, resource_att_d):
    # Rimuovi elementi dal vettore
    nuovo_hyp = rm_vect_element(hyp, list_of_index, m, resource_att_d)

    # Aggiorna il dizionario degli indici del vettore
    new_list_of_index = remove_n_prefixes(list_of_index, m)

    # Calcola il numero totale di elementi rimossi
    # Ogni blocco risorsa ha la lunghezza 'm'
    num_elements_to_remove = m * (1 + len(resource_att_d))

    # Aggiorna il dizionario 'indices' traslando gli indici
    nuovo_indices = {'categoric': [], 'numeric': [], 'unknown': []}
    for key, values in indices.items():
        updated_values = []
        for idx in values:
            # Calcola il nuovo indice se è maggiore del numero di elementi rimossi
            if idx >= num_elements_to_remove:
                updated_values.append(idx - num_elements_to_remove)
            # Mantiene gli indici non influenzati dalla rimozione
            elif idx < list_of_index['blocco_prefix'][0]:
                updated_values.append(idx)
        nuovo_indices[key] = updated_values

    return nuovo_hyp, new_list_of_index, nuovo_indices
