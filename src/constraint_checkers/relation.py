# Importazione delle librerie necessarie
import pdb
from src.enums import TraceState
from src.models import CheckerResult


# Funzione mp_responded_existence per il controllo del vincolo respondedExistence
# Descrizione:
def mp_responded_existence(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    pendings = []
    num_fulfillments = 0
    num_violations = 0
    num_pendings = 0

    for event in trace:
        if event["concept:name"] == a:
            A = event
            if eval(activation_rules):
                pendings.append(event)
    for event in trace:
        if len(pendings) == 0:
            break
        if event["concept:name"] == b:
            T = event
            for A in reversed(pendings):
                if eval(correlation_rules):
                    pendings.remove(A)
                    num_fulfillments += 1
    if done:
        num_violations = len(pendings)
    else:
        num_pendings = len(pendings)
    num_activations = num_fulfillments + num_violations + num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations > 0:
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif done and num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_response per il controllo del vincolo response
# Descrizione:
def mp_response(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    pendings = []
    num_fulfillments = 0
    num_violations = 0
    num_pendings = 0

    for event in trace:
        if event["concept:name"] == a:
            A = event
            if eval(activation_rules):
                pendings.append(event)
        if len(pendings) > 0 and event["concept:name"] == b:
            T = event
            for A in reversed(pendings):
                if eval(correlation_rules):
                    pendings.remove(A)
                    num_fulfillments += 1
    if done:
        num_violations = len(pendings)
    else:
        num_pendings = len(pendings)
    num_activations = num_fulfillments + num_violations + num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_pendings > 0:
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_pendings == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif done and num_violations > 0:
        state = TraceState.VIOLATED
    elif done and num_violations == 0:
        state = TraceState.SATISFIED

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_alternate_response per il controllo del vincolo alternateResponse
# Descrizione:
def mp_alternate_response(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    pending = None
    num_activations = 0
    num_fulfillments = 0
    num_pendings = 0

    for event in trace:
        if event["concept:name"] == a:
            A = event
            if eval(activation_rules):
                pending = event
                num_activations += 1
        if event["concept:name"] == b and pending is not None:
            A = pending
            T = event
            if eval(correlation_rules):
                pending = None
                num_fulfillments += 1
    if not done and pending is not None:
        num_pendings = 1
    num_violations = num_activations - num_fulfillments - num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0 and num_pendings > 0:
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0 and num_pendings == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0 or (done and num_pendings > 0):
        state = TraceState.VIOLATED
    elif done and num_violations == 0 and num_pendings == 0:
        state = TraceState.SATISFIED

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_chain_response per il controllo del vincolo chainResponse
# Descrizione:
def mp_chain_response(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_fulfillments = 0
    num_pendings = 0

    for index, event in enumerate(trace):
        if event["concept:name"] == a:
            A = event
            if eval(activation_rules):
                num_activations += 1
                if index < len(trace) - 1:
                    if trace[index + 1]["concept:name"] == b:
                        T = trace[index + 1]
                        if eval(correlation_rules):
                            num_fulfillments += 1
                else:
                    if not done:
                        num_pendings = 1
    num_violations = num_activations - num_fulfillments - num_pendings

    state = None
    if not vacuous_satisfaction and num_activations == 0:
        if done:
            state = TraceState.VIOLATED
        else:
            state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0 and num_pendings > 0:
        state = TraceState.POSSIBLY_VIOLATED
    elif not done and num_violations == 0 and num_pendings == 0:
        state = TraceState.POSSIBLY_SATISFIED
    elif num_violations > 0 or (done and num_pendings > 0):
        state = TraceState.VIOLATED
    elif done and num_violations == 0 and num_pendings == 0:
        state = TraceState.SATISFIED

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=num_pendings,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_precedence per il controllo del vincolo precedence
# Descrizione:
def mp_precedence(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_fulfillments = 0
    Ts = []

    for event in trace:
        if event["concept:name"] == a:
            Ts.append(event)
        if event["concept:name"] == b:
            A = event
            if eval(activation_rules):
                num_activations += 1
                for T in Ts:
                    if eval(correlation_rules):
                        num_fulfillments += 1
                        break
    num_violations = num_activations - num_fulfillments

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

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=None,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_alternate_precedence per il controllo del vincolo alternatePrecedence
# Descrizione:
def mp_alternate_precedence(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_fulfillments = 0
    Ts = []

    for event in trace:
        if event["concept:name"] == a:
            Ts.append(event)
        if event["concept:name"] == b:
            A = event
            if eval(activation_rules):
                num_activations += 1
                for T in Ts:
                    if eval(correlation_rules):
                        num_fulfillments += 1
                        break
                Ts = []
    num_violations = num_activations - num_fulfillments

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

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=None,
                         num_activations=num_activations,
                         state=state)


# Funzione mp_chain_precedence per il controllo del vincolo chainPrecedence
# Descrizione:
def mp_chain_precedence(trace, done, a, b, rules):
    activation_rules = rules["activation"]
    correlation_rules = rules["correlation"]
    vacuous_satisfaction = rules["vacuous_satisfaction"]

    num_activations = 0
    num_fulfillments = 0

    for index, event in enumerate(trace):
        if event["concept:name"] == b:
            A = event
            if eval(activation_rules):
                num_activations += 1
                if index != 0 and trace[index - 1]["concept:name"] == a:
                    T = trace[index - 1]
                    if eval(correlation_rules):
                        num_fulfillments += 1
    num_violations = num_activations - num_fulfillments

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

    return CheckerResult(num_fulfillments=num_fulfillments,
                         num_violations=num_violations,
                         num_pendings=None,
                         num_activations=num_activations,
                         state=state)
