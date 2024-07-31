import numpy as np


def array_index(n, trace_att_d, resource_att_d):
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

def array_index(n, trace_att_d, resource_att_d):
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

def rm_vect_element(hyp, list_of_index, m, resource_att_d):
    special_value = -999
    if not isinstance(hyp, np.ndarray):
        hyp = np.array(hyp)

    # Determina gli indici da segnare con il valore speciale
    indici_da_segnare = []
    if m <= len(list_of_index.get('blocco_prefix', [])):
        indici_da_segnare.extend(list_of_index['blocco_prefix'][:m])
    else:
        indici_da_segnare.extend(list_of_index.get('blocco_prefix', []))

    # Itera su ciascun blocco risorsa dinamico
    for i in range(len(resource_att_d)):
        block_name = f'blocco_risorsa_{i + 1}'
        if block_name in list_of_index:
            risorsa_indici = list_of_index[block_name]
            if m <= len(risorsa_indici):
                indici_da_segnare.extend(risorsa_indici[:m])
            else:
                indici_da_segnare.extend(risorsa_indici)

    # Filtra gli indici che sono entro i limiti di hyp
    indici_da_segnare = [i for i in indici_da_segnare if i < len(hyp)]

    # Sostituisce gli indici specificati con il valore speciale
    hyp[indici_da_segnare] = special_value

    return hyp
