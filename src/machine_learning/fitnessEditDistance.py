import editdistance  # Importa la libreria per calcolare la distanza di edit
import itertools

# Definizione della funzione edit con due parametri ref e hyp
def edit(ref, hyp):
    ref2 = ref.copy()  # Crea una copia della lista ref
    hyp2 = hyp.copy()  # Crea una copia della lista hyp
    negative_values = []  # Inizializza una lista per i valori negativi
    negative_indexes = []  # Inizializza una lista per gli indici corrispondenti ai valori negativi

    maxi = max(len(ref2), len(hyp2))  # Calcola il massimo tra le lunghezze di ref2 e hyp2

    # Scansiona la lista ref2
    for i in range(len(ref2)):
        if isinstance(ref2[i], list):  # Controlla se l'elemento è una lista
            negative_values.append(ref2[i])  # Aggiungi la lista negative_values
            num_elements = len(ref2[i])  # Ottieni il numero di elementi nella lista negativa
            # Estendi la lista negative_indexes con gli indici duplicati
            negative_indexes.extend([i] * num_elements)
            ref2[i] = ''  # Sostituisci l'elemento con una stringa vuota

    # Unisci tutti gli elementi della lista negative_values in una lista piatta
    negative_values = list(itertools.chain.from_iterable(negative_values))

    # Itera all'indietro attraverso gli elementi di ref2
    for i in range(len(ref)-1, -1, -1):
        if ref2[i] == "" or ref2[i] == 0:  # Controlla se l'elemento in ref è vuoto o zero
            ref2.pop(i)  # Rimuovi l'elemento vuoto o zero da ref2
            hyp2.pop(i)  # Rimuovi l'elemento corrispondente da hyp2

    ed = editdistance.eval(ref2, hyp2)  # Calcola la distanza di edit tra ref2 e hyp2

    # Itera attraverso i valori negativi
    for i in range(len(negative_values)):
        value = abs(negative_values[i])  # Ottieni il valore assoluto
        index = negative_indexes[i]  # Ottieni l'indice corrispondente
        if hyp[index] == value:  # Controlla se il valore in hyp corrisponde al valore negativo
            ed = ed + 1  # Incrementa la distanza di edit

    ed_ratio = ed / maxi  # Calcola il rapporto tra la distanza di edit e la lunghezza massima
    return 1 - ed_ratio  # Restituisci 1 meno il rapporto della distanza di edit
