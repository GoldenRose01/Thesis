# Importazione dei moduli TraceState e CheckerResult dalla directory src.enums e src.models
from src.enums import TraceState
from src.models import CheckerResult

# Funzione mp-choice per il controllo del vincolo
# Descrizione:
def mp_choice(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Inizializzazione di una variabile booleana 'a_or_b_occurs' a False
    a_or_b_occurs = False

    # Iterazione su ogni evento 'A' nella traccia 'trace'
    for A in trace:
        # Verifica se l'evento 'A' ha lo stesso nome di 'a' o 'b'
        if A["concept:name"] == a or A["concept:name"] == b:
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                a_or_b_occurs = True
                break

    # Inizializzazione della variabile 'state' a None
    state = None

    # Calcolo dello stato in base alle condizioni
    if not done and not a_or_b_occurs:
        state = TraceState.POSSIBLY_VIOLATED
    elif done and not a_or_b_occurs:
        state = TraceState.VIOLATED
    elif a_or_b_occurs:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None, num_violations=None, num_pendings=None, num_activations=None, state=state)


# Funzione mp-exclusive-choice per il controllo del vincolo
# Descrizione:
def mp_exclusive_choice(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Inizializzazione delle variabili booleane 'a_occurs' e 'b_occurs' a False
    a_occurs = False
    b_occurs = False

    # Iterazione su ogni evento 'A' nella traccia 'trace'
    for A in trace:
        # Verifica se l'evento 'A' ha lo stesso nome di 'a'
        if not a_occurs and A["concept:name"] == a:
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                a_occurs = True
        # Verifica se l'evento 'A' ha lo stesso nome di 'b'
        if not b_occurs and A["concept:name"] == b:
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                b_occurs = True
        # Se entrambi 'a_occurs' e 'b_occurs' sono True, interrompi la ricerca
        if a_occurs and b_occurs:
            break

    # Inizializzazione della variabile 'state' a None
    state = None

    # Calcolo dello stato in base alle condizioni
    if not done and (not a_occurs and not b_occurs):
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and (a_occurs ^ b_occurs):
        state = TraceState.POSSIBLY_SATISFIED
    elif (a_occurs and b_occurs) or (done and (not a_occurs and not b_occurs)):
        state = TraceState.VIOLATED
    elif done and (a_occurs ^ b_occurs):
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None, num_violations=None, num_pendings=None, num_activations=None, state=state)
