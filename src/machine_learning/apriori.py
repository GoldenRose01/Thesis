from itertools import combinations
from collections import defaultdict


# Funzione per ottenere eventi frequenti
def get_frequent_events(log, support_threshold):
    # Dizionario per contare la frequenza degli eventi
    res = defaultdict(lambda: 0, {})

    # Iterazione attraverso le tracce nel log
    for trace in log:
        for event in trace:
            event_name = event["concept:name"]
            res[event_name] += 1

    # Lista per gli eventi frequenti
    frequent_events = []

    # Filtraggio degli eventi frequenti in base alla soglia di supporto
    for key in res:
        if res[key] / len(log) > support_threshold:
            frequent_events.append(key)

    return frequent_events


# Funzione per ottenere coppie di eventi frequenti
def get_frequent_pairs(log, pairs, support_threshold):
    # Dizionario per contare la frequenza delle coppie di eventi
    res = defaultdict(lambda: 0, {})

    # Iterazione attraverso le tracce nel log
    for trace in log:
        for pair in pairs:
            a_exists = False
            b_exists = False

            # Verifica se gli eventi nella coppia sono presenti nella traccia
            for event in trace:
                if not a_exists and event["concept:name"] == pair[0]:
                    a_exists = True
                elif not b_exists and event["concept:name"] == pair[1]:
                    b_exists = True

                # Se entrambi gli eventi sono stati trovati, aumenta il conteggio
                if a_exists and b_exists:
                    res[pair] += 1
                    break

    # Lista per le coppie di eventi frequenti
    frequent_pairs = []

    # Filtraggio delle coppie di eventi frequenti in base alla soglia di supporto
    for key in res:
        if res[key] / len(log) > support_threshold:
            frequent_pairs.append(key)

    return frequent_pairs


# Funzione per generare eventi e coppie di eventi frequenti
def generate_frequent_events_and_pairs(log, support_threshold):
    print("Ricerca eventi frequenti ...")
    frequent_events = get_frequent_events(log, support_threshold)

    print("Creazione coppie di eventi ...")
    pairs = list(combinations(frequent_events, 2))

    print("Ricerca coppie di eventi frequenti ...")
    frequent_pairs = get_frequent_pairs(log, pairs, support_threshold)

    # Creazione di coppie inverse per ciascuna coppia frequente
    all_frequent_pairs = []
    for pair in frequent_pairs:
        (x, y) = pair
        reverse_pair = (y, x)
        all_frequent_pairs.extend([pair, reverse_pair])

    return frequent_events, all_frequent_pairs
