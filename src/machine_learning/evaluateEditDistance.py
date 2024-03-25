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

def edit_separate(ref, hyp,indices, max_variation):
    # Inizializza la lista delle distanze
    distances = []
    # Correzione: per calcolare correttamente la distanza basata sulla variazione massima per una colonna numerica,
    # abbiamo bisogno di un mapping da indice assoluto a indice relativo nelle colonne numeriche.
    # Creiamo un dizionario per questo scopo.
    index_to_numeric = {abs_index: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    # Calcola la distanza in base al tipo di dato
    for i in range(len(ref)):
        if i in indices['numeric']:
            # Utilizziamo l'indice relativo per ottenere la variazione massima corretta
            rel_index = index_to_numeric[i]  # Ottiene l'indice relativo corrispondente
            # Calcola la distanza basata sulla variazione massima per colonna
            if max_variation[rel_index] != 0:  # Evita divisione per zero
                distance = abs(ref[i] - hyp[0][i]) / max_variation[rel_index]
            else:
                distance = 0
        elif i in indices['categoric'] or i in indices['unknown']:
            # Per dati categorici e sconosciuti: 0 se uguali, 1 se diversi
            distance = 0 if ref[i] == hyp[0][i] else 1
        else:
            # Per sicurezza, ma tutti gli indici dovrebbero essere coperti dalle categorie sopra
            distance = 0
        distances.append(distance)

    # Calcola il rapporto totale della distanza di edit
    ed_ratio = sum(distances) / len(distances) if distances else 0
    return ed_ratio

def weighted_edit_distance(ref, hyp,indices, max_variation):
    # Calcola la distanza di edit con i pesi di trace_attributes,event e resource_attributes
    weighted_distances = []

    # Mapping dei pesi per ogni indice basato sui segmenti
    weights = {}
    for i in indices['complex']:
        weights[i] = wtrace_att
    for i in indices['prefix']:
        weights[i] = wsimple_encoding
    for i in indices['resource']:
        weights[i] = wresource_att

    # Correzione per mappare indici numerici a indici relativi
    index_to_numeric = {abs_index: rel_index for rel_index, abs_index in enumerate(indices['numeric'])}

    for i in range(len(ref)):
        if i in indices['numeric']:
            # Calcolo della distanza per dati numerici
            rel_index = index_to_numeric[i]
            if max_variation[rel_index] != 0:
                distance = abs(ref[i] - hyp[i]) / max_variation[rel_index]
            else:
                distance = 0
        elif i in indices['categoric'] or i in indices['unknown']:
            # Distanza per dati categorici e sconosciuti
            distance = 0 if ref[i] == hyp[i] else 1
        else:
            # Precauzione, tutti gli indici dovrebbero essere coperti
            distance = 0

        # Applica il peso basato sul segmento di appartenenza
        weighted_distance = distance * weights.get(i, 1)  # Default weight is 1 if not in complex/prefix/resource
        weighted_distances.append(weighted_distance)

    # Calcolo del rapporto totale della distanza di edit ponderata
    weighted_ed_ratio = sum(weighted_distances) / len(weighted_distances) if weighted_distances else 0

    return weighted_ed_ratio