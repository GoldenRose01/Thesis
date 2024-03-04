import re
def clean_lists(lista):
    # Definizione dell'espressione regolare per identificare i suffissi numerici
    pattern = re.compile(r"(.*)_\d+$")

    # Set per mantenere gli attributi unici senza suffissi numerici
    attributi_unici = set()

    for attributo in lista:
        # Utilizzo dell'espressione regolare per rimuovere i suffissi numerici
        match = pattern.match(attributo)
        if match:
            # Se c'è un match, aggiungi la parte dell'attributo senza il suffisso numerico
            attributi_unici.add(match.group(1))
        else:
            # Se non c'è un match (nessun suffisso numerico), aggiungi l'attributo così com'è
            attributi_unici.add(attributo)

    # Converti il set in una lista per il risultato finale
    clean_list = list(attributi_unici)
    return clean_list
