# Importazione delle enumerazioni ConstraintChecker e TraceState,
# e della classe CheckerResult dalla directory src.enums e src.models
from src.enums.ConstraintChecker import ConstraintChecker
from src.enums import TraceState
from src.models import CheckerResult


# Funzione mp-existence per il controllo del vincolo
# Descrizione:
# Il vincolo di esistenza futura existence(n, a) indica che
# l'evento 'a' deve verificarsi almeno n volte nella traccia.
def mp_existence(trace, done, a, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Estrazione del valore di 'n' corrispondente all'enumerazione ConstraintChecker.EXISTENCE
    n = rules["n"][ConstraintChecker.EXISTENCE]

    # Inizializzazione del conteggio 'num_activations' a 0
    num_activations = 0

    # Iterazione su ogni evento 'A' nella traccia 'trace'
    for A in trace:
        # Verifica se l'evento 'A' ha lo stesso nome di 'a' e soddisfa le regole di attivazione
        if A["concept:name"] == a and eval(activation_rules):
            num_activations += 1

    # Inizializzazione della variabile 'state' a None
    state = None

    # Calcolo dello stato in base alle condizioni
    if not done and num_activations < n:
        state = TraceState.POSSIBLY_VIOLATED
    elif done and num_activations < n:
        state = TraceState.VIOLATED
    elif num_activations >= n:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None, num_violations=None, num_pendings=None, num_activations=None,
                         state=state)


# Funzione mp-absence per il controllo del vincolo
# Descrizione:
# Il vincolo di assenza futura absence(n + 1, a) indica che
# l'evento 'a' può verificarsi al massimo n volte nella traccia.
def mp_absence(trace, done, a, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Estrazione del valore di 'n' corrispondente all'enumerazione ConstraintChecker.ABSENCE
    n = rules["n"][ConstraintChecker.ABSENCE]

    # Inizializzazione del conteggio 'num_activations' a 0
    num_activations = 0

    # Iterazione su ogni evento 'A' nella traccia 'trace'
    for A in trace:
        # Verifica se l'evento 'A' ha lo stesso nome di 'a' e soddisfa le regole di attivazione
        if A["concept:name"] == a and eval(activation_rules):
            num_activations += 1

    # Inizializzazione della variabile 'state' a None
    state = None

    # Calcolo dello stato in base alle condizioni
    if not done and num_activations < n:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_activations >= n:
        state = TraceState.VIOLATED
    elif done and num_activations < n:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None, num_violations=None, num_pendings=None, num_activations=None,
                         state=state)


# Funzione mp-init per il controllo del vincolo
# Descrizione:
# Il vincolo di inizializzazione futura init(e) indica che
# l'evento 'e' è il primo evento che si verifica nella traccia.
def mp_init(trace, done, a, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Inizializzazione della variabile 'state' a TraceState.VIOLATED
    state = TraceState.VIOLATED

    # Verifica se il primo evento nella traccia ha lo stesso nome di 'a'
    if trace[0]["concept:name"] == a:
        A = trace[0]
        # Valutazione delle regole di attivazione tramite 'eval'
        if eval(activation_rules):
            state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None, num_violations=None, num_pendings=None, num_activations=None,
                         state=state)


# Funzione mp-exactly per il controllo del vincolo
# Descrizione:
# Il vincolo di esistenza futura exacty(n, a) indica che
# l'evento 'a' deve verificarsi esattamente n volte nella traccia.
def mp_exactly(trace, done, a, rules):
    # Estrazione delle regole di attivazione dal dizionario 'rules'
    activation_rules = rules["activation"]

    # Estrazione del valore di 'n' corrispondente all'enumerazione ConstraintChecker.EXACTLY
    n = rules["n"][ConstraintChecker.EXACTLY]

    # Inizializzazione del conteggio 'num_activations' a 0
    num_activations = 0

    # Iterazione su ogni evento 'A' nella traccia 'trace'
    for A in trace:
        # Verifica se l'evento 'A' ha lo stesso nome di 'a' e soddisfa le regole di attivazione
        if A["concept:name"] == a and eval(activation_rules):
            num_activations += 1

    # Inizializzazione della variabile 'state' a None
    state = None

    # Calcolo dello stato in base alle condizioni
    if not done and num_activations < n:
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_activations == n:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_activations > n or (done and num_activations < n):
        state = TraceState.VIOLATED
    elif done and num_activations == n:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi a None e stato calcolato
    return CheckerResult(num_fulfillments=None,
                         num_violations=None,
                         num_pendings=None,
                         num_activations=None,
                         state=state)
