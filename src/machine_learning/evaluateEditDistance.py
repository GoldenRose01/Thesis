import editdistance  # Importa la libreria per calcolare la distanza di edit
import itertools
from settings import Print_edit_distance

def edit(ref, hyp):#numerical e categorical erano stati presi per una prova di extract a posteriori

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

def edit_separate(ref, hyp):
    # Inizializza la lista delle distanze
    distances = []

    # Per dati categorici: 0 se uguali, 1 se diversi
    distances = [0 if ref[i] == hyp[i] else 1 for i in range(len(ref))]

    # Per dati numerici: calcola la distanza basata sulla variazione massima per posizione
    for i in range(len(ref)):
        # Trova la variazione massima per la posizione corrente
        all_values = [hyp_instance[i] for hyp_instance in hyp] + [ref[i]]
        max_variation = max(all_values) - min(all_values)
        # Calcola la distanza per la posizione corrente
        distance = abs(ref[i] - hyp[0][i]) / max_variation if max_variation else 0
        distances.append(distance)

    # Calcola il rapporto totale della distanza di edit
    ed_ratio = sum(distances) / len(distances) if distances else 0
    return ed_ratio
