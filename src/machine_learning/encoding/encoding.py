from src.machine_learning.encoding.feature_encoder.frequency_features   import frequency_features
from src.machine_learning.encoding.feature_encoder.simple_features      import simple_features
from src.machine_learning.encoding.feature_encoder.complex_features     import complex_features
from src.machine_learning.encoding.data_encoder                         import *
from src.machine_learning.encoding.constants                            import EncodingType
from src.machine_learning.label.common                                  import LabelTypes
from src.machine_learning.utils                                         import *
from src.models.DTInput                                                 import *
from pandas                                                             import DataFrame
import settings

TRACE_TO_DF = {
    EncodingType.SIMPLE.value: simple_features,
    EncodingType.FREQUENCY.value: frequency_features,
    EncodingType.COMPLEX.value: complex_features,
    #todo EncodingType.DECLARE.value : declare_features
}


# Definisce una classe chiamata 'Encoding'
class Encoding:
    def __init__(self, log: DataFrame = None):

        case_counts = {}

        # Itera attraverso le tracce e conta il numero di tracce per ogni caso
        for trace in log:
            case_id = trace.attributes['concept:name']
            for idx, event in enumerate(trace):
                if case_id in case_counts:
                    case_counts[case_id] += 1
                else:
                    case_counts[case_id] = 1

        total_cases = len(case_counts)
        total_counts = sum(case_counts.values())

        # Calcola la media
        if total_cases > 0:
            average = total_counts / total_cases
        else:
            average = 0

        self.prefix = int(average)  # Calcola il prefisso basato sulla media
        print(self.prefix)

        self.CONF = {
            'data': log,
            'prefix_length_strategy': 'fixed',
            'prefix_length': self.prefix,
            'padding': True,
            'feature_selection': settings.type_encoding,
            'task_generation_type': 'all_in_one',
            'attribute_encoding': 'label',
            'labeling_type': LabelTypes.ATTRIBUTE_STRING,
        }

        train_cols: DataFrame = None

        # Crea un DataFrame 'df' basato sulla strategia di encoding selezionata
        if self.CONF['feature_selection'] == 'complex':
            self.df, self.index = TRACE_TO_DF[self.CONF['feature_selection']](
                log,
                prefix_length=self.CONF['prefix_length'],
                padding=self.CONF['padding'],
                prefix_length_strategy=self.CONF['prefix_length_strategy'],
                labeling_type=self.CONF['labeling_type'],
                generation_type=self.CONF['task_generation_type'],
                feature_list=train_cols,
                target_event=None
            )
        else:
            self.df = TRACE_TO_DF[self.CONF['feature_selection']](
                log,
                prefix_length=self.CONF['prefix_length'],
                padding=self.CONF['padding'],
                prefix_length_strategy=self.CONF['prefix_length_strategy'],
                labeling_type=self.CONF['labeling_type'],
                generation_type=self.CONF['task_generation_type'],
                feature_list=train_cols,
                target_event=None
            )


        self.encoder = Encoder(df=self.df, attribute_encoding=self.CONF['attribute_encoding'])
        self.encoded = 0


    # Metodo per codificare le tracce
    def encode_traces(self, numeric_columns, categoric_columns):
        self.encoder.encode(df=self.df)

        features = []
        encoded_data = []
        labels = []
        column_names = list(self.df.columns[0:len(self.df.columns) - 1])
        for index, row in self.df.iterrows():
            labels.append(int(row['label']) - 1)
            trace_data = list(row[0:len(self.df.columns)-1])

            # Converti eventuali liste in tuple
            trace_data = [tuple(data) if isinstance(data, list) else data for data in trace_data]

            encoded_data.append(trace_data)
        if not features:
            features = list(column_names)

        (ncu_data,indices,max_variations) = self.separate_and_encode(encoded_data,features,numeric_columns, categoric_columns)

        if self.CONF['feature_selection'] == 'complex':
            for key, values in self.index.items():
                # Se la chiave esiste già in indices, uniamo le liste (assicurandoci che siano uniche)
                if key in indices:
                    indices[key] = list(set(indices[key] + values))
                else:
                    # Altrimenti, aggiungiamo direttamente la lista a indices sotto la nuova chiave
                    indices[key] = values

        return DTInput(features, encoded_data, labels), self.prefix, ncu_data,indices,max_variations

    # Funzione per separare e codificare i dati in vettori categorici e numerici
    def separate_and_encode(self,encoded_data, features, numeric_columns, categoric_columns):
        # Inizializzazione delle liste per dati numerici, categorici e sconosciuti
        numeric_data = []
        categoric_data = []
        unknown_data = []

        # Organize data into a dictionary
        ncu_data = {
            'numeric': numeric_data,
            'categoric': categoric_data,
            'unknown': unknown_data
        }

        # Distinguiamo tra colonne numeriche, categoriche esplicite e il resto come unknown
        numeric_columns_set = set(numeric_columns)
        categoric_columns_set = set(categoric_columns)

        # Calcoliamo gli indici per ogni tipo di colonna
        numeric_indices = [index for index, feature in enumerate(features) if feature in numeric_columns_set]
        categoric_indices = [index for index, feature in enumerate(features) if feature in categoric_columns_set]
        unknown_indices = [index for index, feature in enumerate(features) if
                           feature not in numeric_columns_set and feature not in categoric_columns_set]

        # Organize indices into another dictionary
        indices = {
            'numeric': numeric_indices,
            'categoric': categoric_indices,
            'unknown': unknown_indices
        }

        # Estrazione dei dati per ogni categoria
        for row in encoded_data:
            numeric_data.append([row[index] for index in numeric_indices])
            categoric_data.append([row[index] for index in categoric_indices])
            unknown_data.append([row[index] for index in unknown_indices])
        # Calcolo del max e min per le colonne dei dati numerici
        max_values = [max(column) for column in zip(*numeric_data)]
        min_values = [min(column) for column in zip(*numeric_data)]

        # Calcolo della variazione massima per ogni colonna numerica
        max_variations = [max_val - min_val for max_val, min_val in zip(max_values, min_values)]

        return ncu_data, indices, max_variations


    # Metodo per decodificare un log codificato
    # Funzione per convertire dati in tuple se sono liste
    def convert_data_to_hashable(data):
        if isinstance(data, list):
            return tuple(data)
        return data

    # Modifica la funzione Encoding.decode
    def decode(self, log):
        prefix_columns = {}
        for i, prefix in enumerate(log):
            column_name = f'prefix_{i + 1}'
            prefix_columns[column_name] = [prefix]
        df_input = pd.DataFrame(prefix_columns)
        self.encoder.decode(df=df_input)
        return df_input

    # Modifica la funzione Encoding.encode
    def encode(self, log):
        prefix_columns = {}
        for i, prefix in enumerate(log):
            column_name = f'prefix_{i + 1}'
            prefix_columns[column_name] = [prefix]
        df_input = pd.DataFrame(prefix_columns)
        self.encoder.encode(df=df_input)
        return df_input