import editdistance  # Importa la libreria per calcolare la distanza di edit
import itertools
from settings import Print_edit_distance, wtrace_att, wsimple_encoding, wresource_att

def edit(ref, hyp):

    ref2 = ref.copy()
    hyp2 = hyp.copy()

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
    if Print_edit_distance==True:
        print("Ed tramite Libreria:"+ str(ed_ratio))

    return ed_ratio


def edit_separate(ref, hyp, indices, max_variation):
    # Inizializza la lista delle distanze
    distances = []
    # Mapping da indice in indices a indice in ref/hyp per le colonne numeriche
    index_to_numeric = {abs_index - 1: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    for i in range(len(ref)):
        adjusted_index = i + 1  # Aggiusta l'indice per matchare con quello in indices
        if adjusted_index in indices['numeric']:
            # Usa l'indice aggiustato per ottenere la variazione massima corretta
            rel_index = index_to_numeric[i]  # Usa l'indice originale di ref/hyp
            if max_variation[rel_index] != 0:
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

def weighted_edit_distance(ref, hyp, indices, max_variation):
    weighted_distances = []
    weights = {}

    for i in indices['complex']:
        weights[i - 1] = wtrace_att  # Aggiusta l'indice per i pesi
    for i in indices['prefix']:
        weights[i - 1] = wsimple_encoding
    for i in indices['resource']:
        weights[i - 1] = wresource_att

    index_to_numeric = {abs_index - 1: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    for i in range(len(ref)):
        adjusted_index = i + 1
        if adjusted_index in indices['numeric']:
            rel_index = index_to_numeric[i]
            if max_variation[rel_index] != 0:
                distance = abs(ref[i] - hyp[i]) / max_variation[rel_index]
            else:
                distance = 0
        elif adjusted_index in indices['categoric'] or adjusted_index in indices['unknown']:
            distance = 0 if ref[i] == hyp[i] else 1
        else:
            distance = 0

        weighted_distance = distance * weights.get(i, 1)  # Applica peso default se non specificato
        weighted_distances.append(weighted_distance)

    weighted_ed_ratio = sum(weighted_distances) / len(weighted_distances) if weighted_distances else 0

    return weighted_ed_ratio