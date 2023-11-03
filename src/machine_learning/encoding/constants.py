from enum import Enum  # Importa la classe Enum dal modulo enum

# Definisce un'enumerazione per il tipo di codifica
class EncodingType(Enum):
	SIMPLE = 'simple'
	FREQUENCY = 'frequency'
	COMPLEX = 'complex'
	DECLARE = 'declare'

# Definisce un'enumerazione per il tipo di attributo di codifica
class EncodingTypeAttribute(Enum):
	LABEL = 'label'
	ONEHOT = 'onehot'

# Definisce un'enumerazione per il tipo di generazione di attività
class TaskGenerationType(Enum):
	ONLY_THIS = 'only_this'
	ALL_IN_ONE = 'all_in_one'

# Definisce un'enumerazione per la strategia di lunghezza del prefisso
class PrefixLengthStrategy(Enum):
	FIXED = 'fixed'
	PERCENTAGE = 'percentage'
	TARGET_EVENT = 'target_event'

# Questa funzione calcola la lunghezza del prefisso in base alla strategia specificata
def get_prefix_length(trace , prefix_length: float, prefix_length_strategy, target_event=None) -> int:
	if prefix_length_strategy == PrefixLengthStrategy.FIXED.value:
		return int(prefix_length)
	elif prefix_length_strategy == PrefixLengthStrategy.PERCENTAGE.value:
		return int(prefix_length * len(trace))
	elif prefix_length_strategy == PrefixLengthStrategy.TARGET_EVENT.value:
		if target_event is not None:
			try:
				index = [e['concept:name'] for e in trace].index(target_event) + 1
			except ValueError:
				return 0
			return index
		else:
			return 0
	else:
		raise Exception('Wrong prefix_length strategy')

# Questa funzione calcola la lunghezza massima del prefisso in base alla strategia specificata
def get_max_prefix_length(log, prefix_length: float, prefix_length_strategy, target_event) -> int:
	prefix_lengths = [get_prefix_length(trace, prefix_length, prefix_length_strategy, target_event) for trace in log]
	return max(prefix_lengths)
