from src.constants import *
from src.machine_learning.labeling import *
from src.models.DTInput import *
from src.enums.ConstraintChecker import *
import settings
from src.machine_learning.label.common import LabelTypes
from pandas import DataFrame
from src.machine_learning.encoding.constants import EncodingType
from src.machine_learning.encoding.feature_encoder.frequency_features import frequency_features
from src.machine_learning.encoding.feature_encoder.simple_features import simple_features
from src.machine_learning.encoding.feature_encoder.complex_features import complex_features
from src.machine_learning.encoding.data_encoder import *

TRACE_TO_DF = {
    EncodingType.SIMPLE.value: simple_features,
    EncodingType.FREQUENCY.value: frequency_features,
    EncodingType.COMPLEX.value: complex_features,
    # EncodingType.DECLARE.value : declare_features
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
            'feature_selection': 'simple',
            'task_generation_type': 'all_in_one',
            'attribute_encoding': 'label',
            'labeling_type': LabelTypes.ATTRIBUTE_STRING,
        }

        train_cols: DataFrame = None

        # Crea un DataFrame 'df' basato sulla strategia di encoding selezionata
        self.df = TRACE_TO_DF[self.CONF['feature_selection']](
            log,
            prefix_length=self.CONF['prefix_length'],
            padding=self.CONF['padding'],
            prefix_length_strategy=self.CONF['prefix_length_strategy'],
            labeling_type=self.CONF['labeling_type'],
            generation_type=self.CONF['task_generation_type'],
            feature_list=train_cols,
        )

        self.encoder = Encoder(df=self.df, attribute_encoding=self.CONF['attribute_encoding'])
        self.encoded = 0

    # Metodo per codificare le tracce
    def encode_traces(self):
        self.encoder.encode(df=self.df)

        features = []
        encoded_data = []
        labels = []
        column_names = list(self.df.columns[0:self.prefix + 1])
        for index, row in self.df.iterrows():
            labels.append(int(row['label']) - 1)
            encoded_data.append(list(row[0:self.prefix + 1]))
        if not features:
            features = list(column_names)

        return DTInput(features, encoded_data, labels), self.prefix

    # Metodo per decodificare un log codificato
    def decode(self, log):
        prefix_columns = {}
        for i, prefix in enumerate(log):
            column_name = f'prefix_{i + 1}'
            prefix_columns[column_name] = [prefix]
        df_input = pd.DataFrame(prefix_columns)
        self.encoder.decode(df=df_input)
        return df_input

    # Metodo per codificare un log decodificato
    def encode(self, log):
        prefix_columns = {}
        for i, prefix in enumerate(log):
            column_name = f'prefix_{i + 1}'
            prefix_columns[column_name] = [prefix]
        df_input = pd.DataFrame(prefix_columns)
        self.encoder.encode(df=df_input)
        return df_input