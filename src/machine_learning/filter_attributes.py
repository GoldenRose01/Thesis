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
    ta_len=len(trace_att_d)
    p_len=ta_len+n
    ra_len=p_len+(n*len(resource_att_d))
    #dato lunghezza dei blocchi creazione indicizzazione
    list_of_index = {
        'blocco_trace_att'  : list(range(0, ta_len)),
        'blocco_prefix'     : list(range(ta_len, p_len)),
        'blocco_risorsa'    : list(range(p_len, ra_len))
    }

    return list_of_index

def remove_n_prefixes(list_of_index, m):
    # Aggiorna il blocco dei prefissi
    if isinstance(list_of_index['blocco_prefix'], list) and len(list_of_index['blocco_prefix']) > m:
        list_of_index['blocco_prefix'] = list_of_index['blocco_prefix'][m:]
    else:
        list_of_index['blocco_prefix'] = []

        # Aggiorna i blocchi delle risorse
    if isinstance(list_of_index['blocco_risorsa'], list):
        for i in range(len(list_of_index['blocco_risorsa'])):
            if isinstance(list_of_index['blocco_risorsa'][i], list) and len(list_of_index['blocco_risorsa'][i]) > m:
                list_of_index['blocco_risorsa'][i] = list_of_index['blocco_risorsa'][i][m:]
            else:
                list_of_index['blocco_risorsa'][i] = []
    return list_of_index

def rm_vect_element(hyp, list_of_index, m):
    if not isinstance(hyp, np.ndarray):
        hyp = np.array(hyp)

    # Determine indices to be removed
    indici_da_rimuovere = []
    if m <= len(list_of_index['blocco_prefix']):
        indici_da_rimuovere.extend(list_of_index['blocco_prefix'][:m])
    else:
        indici_da_rimuovere.extend(list_of_index['blocco_prefix'])

    for risorsa_indici in list_of_index['blocco_risorsa']:
        if m <= len(risorsa_indici):
            indici_da_rimuovere.extend(risorsa_indici[:m])
        else:
            indici_da_rimuovere.extend(risorsa_indici)

    # Filter indices that are within the bounds of hyp
    indici_da_rimuovere = [i for i in indici_da_rimuovere if i < len(hyp)]

    # Create a boolean mask to keep valid indices
    mask = np.ones(len(hyp), dtype=bool)
    mask[indici_da_rimuovere] = False

    # Apply the mask
    nuovo_hyp = hyp[mask]

    return nuovo_hyp


def update_hyp_indices(hyp, list_of_index, indices, m):
    # Rimuovi elementi dal vettore
    nuovo_hyp = rm_vect_element(hyp, list_of_index, m)

    # Aggiorna il dizionario degli indici del vettore
    nuovo_dizionario = remove_n_prefixes(list_of_index, m)

    # Calcola il numero totale di elementi rimossi (assumendo che ogni risorsa segue la stessa struttura)
    num_elements_to_remove = m * (1 + len(list_of_index['blocco_risorsa']))

    # Aggiorna il dizionario 'indices' traslando gli indici
    nuovo_indices = {'categoric': [], 'numeric': [], 'unknown': []}
    for key, value in indices.items():
        # Aggiorniamo solo gli indici che sono maggiori del numero di elementi rimossi per mantenere la validità
        nuovo_indices[key] = [idx - num_elements_to_remove if idx >= num_elements_to_remove else idx for idx in value if idx >= num_elements_to_remove]

    return nuovo_hyp, nuovo_dizionario, nuovo_indices
