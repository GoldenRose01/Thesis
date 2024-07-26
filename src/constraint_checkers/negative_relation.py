# Importazione delle enumerazioni TraceState e CheckerResult,
# e della classe CheckerResult dalla directory src.enums e src.models
from src.enums import TraceState
from src.models import CheckerResult


# Funzione mp-not-responded-existence per il controllo del vincolo
# Descrizione:
def mp_not_responded_existence(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione, correlazione e vacuous_satisfaction dal dizionario 'rules'
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    pendings = []
    num_fulfillments = 0
    num_violations = 0
    num_pendings = 0

    # Iterazione su ogni evento 'event' nella traccia 'trace'
    for event in trace:
        if event["concept:name"] == a:
            A = event
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                pendings.append(event)
    for event in trace:
        if len(pendings) == 0:
            break
        if event["concept:name"] == b:
            T = event
            for A in reversed(pendings):
                # Valutazione delle regole di correlazione tramite 'eval'
                if eval(correlation_rules):
                    pendings.remove(A)
                    num_violations += 1
    if done:
        num_fulfillments = len(pendings)
    else:
        num_pendings = len(pendings)
    num_activations = num_fulfillments + num_violations + num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi e stato calcolato
    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp-not-response per il controllo del vincolo
# Descrizione:
def mp_not_response(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione, correlazione e vacuous_satisfaction dal dizionario 'rules'
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    pendings = []
    num_fulfillments = 0
    num_violations = 0
    num_pendings = 0

    # Iterazione su ogni evento 'event' nella traccia 'trace'
    for event in trace:
        if event["concept:name"] == a:
            A = event
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                pendings.append(event)
        if len(pendings) > 0 and event["concept:name"] == b:
            T = event
            for A in reversed(pendings):
                # Valutazione delle regole di correlazione tramite 'eval'
                if eval(correlation_rules):
                    pendings.remove(A)
                    num_violations += 1
    if done:
        num_fulfillments = len(pendings)
    else:
        num_pendings = len(pendings)
    num_activations = num_fulfillments + num_violations + num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi e stato calcolato
    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp-not-chain-response per il controllo del vincolo
# Descrizione:
def mp_not_chain_response(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione, correlazione e vacuous_satisfaction dal dizionario 'rules'
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_violations = 0
    num_pendings = 0

    # Iterazione su ogni evento 'event' nella traccia 'trace' utilizzando l'indice 'index'
    for index, event in enumerate(trace):
        if event["concept:name"] == a:
            A = event
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                num_activations += 1
                if index < len(trace) - 1:
                    if trace[index + 1]["concept:name"] == b:
                        T = trace[index + 1]
                        # Valutazione delle regole di correlazione tramite 'eval'
                        if eval(correlation_rules):
                            num_violations += 1
                else:
                    if not done:
                        num_pendings = 1
    num_fulfillments = num_activations - num_violations - num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi e stato calcolato
    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp-not-precedence per il controllo del vincolo
# Descrizione:
def mp_not_precedence(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione, correlazione e vacuous_satisfaction dal dizionario 'rules'
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_violations = 0
    Ts = []

    # Iterazione su ogni evento 'event' nella traccia 'trace'
    for event in trace:
        if event["concept:name"] == a:
            Ts.append(event)
        if event["concept:name"] == b:
            A = event
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                num_activations += 1
                for T in Ts:
                    # Valutazione delle regole di correlazione tramite 'eval'
                    if eval(correlation_rules):
                        num_violations += 1
                        break
    num_fulfillments = num_activations - num_violations

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi e stato calcolato
    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=None,
                         num_activations=num_activations,
                         state=state)


# Funzione mp-not-chain-precedence per il controllo del vincolo
# Descrizione:
def mp_not_chain_precedence(trace, done, a, b, rules):
    # Estrazione delle regole di attivazione, correlazione e vacuous_satisfaction dal dizionario 'rules'
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_violations = 0

    # Iterazione su ogni evento 'event' nella traccia 'trace' utilizzando l'indice 'index'
    for index, event in enumerate(trace):
        if event["concept:name"] == b:
            A = event
            # Valutazione delle regole di attivazione tramite 'eval'
            if eval(activation_rules):
                num_activations += 1
                if index != 0 and trace[index - 1]["concept:name"] == a:
                    T = trace[index - 1]
                    # Valutazione delle regole di correlazione tramite 'eval'
                    if eval(correlation_rules):
                        num_violations += 1
    num_fulfillments = num_activations - num_violations

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    # Restituzione di un oggetto CheckerResult con conteggi e stato calcolato
    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=None,
                         num_activations=num_activations,
                         state=state)
