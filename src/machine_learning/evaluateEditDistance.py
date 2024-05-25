import editdistance  # Importa la libreria per calcolare la distanza di edit
import itertools
from settings import Print_edit_distance, wtrace_att, wactivities, wresource_att

def edit(ref, hyp, special_value=-999):
    ref2 = [x for x in ref if x != special_value]
    hyp2 = [x for x in hyp if x != special_value]

    hyp2 = hyp2[:len(ref2)]  # Limita la lunghezza di hyp2 alla lunghezza di ref2
    hyp2 = [int(elemento) for elemento in hyp2]  # Converte gli elementi di hyp2 in interi

    maxi = max(len(ref2), len(hyp2))

    for i in range(len(ref2)-1, -1, -1):
        if (ref2[i] == "" or ref2[i] == 0) and i < len(hyp2):
            ref2.pop(i)
            hyp2.pop(i)

    # Calcola la distanza di edit con la libreria editdistance
    ed_lib = editdistance.eval(ref2, hyp2)

    # Calcola il rapporto totale della distanza di edit utilizzando solo le tue regole
    ed_ratio = ed_lib / maxi

    return ed_ratio

def edit_separate(ref, hyp, indices, max_variation, special_value=-999):
    # Inizializza la lista delle distanze
    distances = []
    # Mapping da indice in indices a indice in ref/hyp per le colonne numeriche
    index_to_numeric = {abs_index - 1: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    # Assicura che il loop non ecceda la lunghezza delle liste ref e hyp
    min_length = min(len(ref), len(hyp))

    for i in range(min_length):
        if ref[i] == special_value or hyp[i] == special_value:
            continue

        adjusted_index = i + 1  # Aggiusta l'indice per matchare con quello in indices
        if adjusted_index in indices['numeric']:
            # Usa l'indice aggiustato per ottenere la variazione massima corretta
            rel_index = index_to_numeric.get(i, None)  # Usa l'indice originale di ref/hyp
            if rel_index is not None and max_variation[rel_index] != 0:
                distance = abs(ref[i] - hyp[i]) / max_variation[rel_index]
            else:
                distance = 0
        elif adjusted_index in indices['categoric'] or adjusted_index in indices['unknown']:
            distance = 0 if ref[i] == hyp[i] else 1
        else:
            distance = 0
        distances.append(distance)

    ed_ratio = sum(distances) / len(distances) if distances else 0
    return ed_ratio
def weighted_edit_distance(ref, hyp, indices, max_variation, length_t, special_value=-999):
    weighted_distances = []
    weights = {}

    # Loop per assegnare i pesi
    for i in range(length_t):
        weights[i] = wtrace_att
    for i in indices['prefix']:
        weights[i] = wactivities
    for i in indices['resource']:
        weights[i] = wresource_att

    index_to_numeric = {abs_index - 1: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    # Assicura che il loop non ecceda la lunghezza delle liste ref e hyp
    min_length = min(len(ref), len(hyp))

    for i in range(min_length):
        if ref[i] == special_value or hyp[i] == special_value:
            continue

        adjusted_index = i + 1

        # Converti ref[i] e hyp[i] a numerici se non lo sono già
        try:
            numeric_ref = float(ref[i])
            numeric_hyp = float(hyp[i])
        except ValueError:
            print(f"Skipping non-numeric data at index {i}: ref[i]={ref[i]}, hyp[i]={hyp[i]}")
            continue

        if adjusted_index in indices['numeric']:
            rel_index = index_to_numeric.get(i, None)
            if rel_index is not None and max_variation[rel_index] != 0:
                distance = abs(numeric_ref - numeric_hyp) / max_variation[rel_index]
            else:
                distance = 0
        elif adjusted_index in indices['categoric'] or adjusted_index in indices['unknown']:
            distance = 0 if numeric_ref == numeric_hyp else 1
        else:
            distance = 0

        weighted_distance = distance * weights.get(i, 1)  # Applica peso default se non specificato
        weighted_distances.append(weighted_distance)

    weighted_ed_ratio = sum(weighted_distances) / len(weighted_distances) if weighted_distances else 0

    return weighted_ed_ratio

