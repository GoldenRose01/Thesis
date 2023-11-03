import editdistance  # Importa la libreria per calcolare la distanza di edit
import itertools

# Definizione della funzione edit con due parametri ref e hyp
def edit(ref, hyp):

    ref2 = ref.copy()  # Crea una copia della lista ref
    hyp2 = hyp.copy()  # Crea una copia della lista hyp
    hyp2 = hyp2[:len(ref2)]  # Limita la lunghezza di hyp2 alla lunghezza di ref2
    hyp2 = [int(elemento) for elemento in hyp2]  # Converte gli elementi di hyp2 in interi

    maxi = max(len(ref2), len(hyp2))  # Calcola il massimo tra le lunghezze di ref2 e hyp2

    for i in range(len(ref)-1, -1, -1):  # Itera all'indietro attraverso gli elementi di ref
        if (ref2[i] == "" or ref2[i] == 0) and i < len(hyp):  # Controlla se l'elemento in ref è vuoto o zero e se è presente nell'indice corrispondente in hyp
            ref2.pop(i)  # Rimuovi l'elemento vuoto o zero da ref2
            hyp2.pop(i)  # Rimuovi l'elemento corrispondente da hyp2

    ed = editdistance.eval(ref2, hyp2)  # Calcola la distanza di edit tra ref2 e hyp2
    ed_ratio = ed / maxi  # Calcola il rapporto tra la distanza di edit ed il massimo delle lunghezze
    return ed_ratio  # Restituisci il rapporto della distanza di edit
