import numpy as np  # Importa il modulo numpy con l'alias 'np'
import pandas as pd  # Importa il modulo pandas con l'alias 'pd'
from pandas import DataFrame  # Importa la classe DataFrame dal modulo pandas
from sklearn.preprocessing import LabelEncoder  # Importa la classe LabelEncoder dal modulo sklearn.preprocessing

PADDING_VALUE = '0'  # Definisce il valore di padding come '0'


# Definisce una classe chiamata 'Encoder'
class Encoder:
    def __init__(self, df: DataFrame = None, attribute_encoding=None):
        self.attribute_encoding = attribute_encoding
        self._encoder = {}  # Dizionario per memorizzare gli encoder
        self._label_dict = {}  # Dizionario per memorizzare le mappe etichetta -> valore numerico
        self._label_dict_decoder = {}  # Dizionario per memorizzare le mappe valore numerico -> etichetta

        # Itera sulle colonne del DataFrame 'df'
        for column in df:
            if column != 'trace_id':
                # Verifica il tipo di dato nella colonna e se è necessario codificarlo
                if df[column].dtype != int or (df[column].dtype == int and np.any(df[column] < 0)):

                    if attribute_encoding == "label":
                        # Crea un oggetto LabelEncoder per la colonna corrente
                        self._encoder[column] = LabelEncoder().fit(
                            sorted(pd.concat([pd.Series([str(PADDING_VALUE)]), df[column].apply(lambda x: str(x))])))

                        # Crea una mappa di etichette a valori numerici
                        classes = self._encoder[column].classes_
                        transforms = self._encoder[column].transform(classes)
                        self._label_dict[column] = dict(zip(classes, transforms))

                        # Crea una mappa di valori numerici a etichette (decodificatore)
                        self._label_dict_decoder[column] = dict(zip(transforms, classes))
                    else:
                        pass

    # Metodo per codificare un DataFrame 'df'
    def encode(self, df: DataFrame) -> None:
        for column in df:
            if column in self._encoder:
                df[column] = df[column].apply(lambda x: self._label_dict[column].get(str(x), PADDING_VALUE))

    # Metodo per decodificare un DataFrame 'df'
    def decode(self, df: DataFrame) -> None:
        for column in df:
            if column in self._encoder:
                df[column] = df[column].apply(
                    lambda x: self._label_dict_decoder[column].get(abs(int(x)), PADDING_VALUE) if x else PADDING_VALUE)

    # Metodo per decodificare una riga di un DataFrame
    def decode_row(self, row) -> np.array:
        decoded_row = []
        for column, value in row.iteritems():
            if column in self._encoder:
                decoded_row += [self._label_dict_decoder[column].get(value, PADDING_VALUE)]
            else:
                decoded_row += [value]
        return np.array(decoded_row)

    # Metodo per decodificare una colonna di un DataFrame
    def decode_column(self, column, column_name) -> np.array:
        decoded_column = []
        if column_name in self._encoder:
            decoded_column += [self._label_dict_decoder[column_name].get(x, PADDING_VALUE) for x in column]
        else:
            decoded_column += list(column)
        return np.array(decoded_column)

    # Metodo per ottenere i valori delle mappe di codifica
    def get_values(self, column_name):
        return (self._label_dict[column_name].keys(), self._label_dict_decoder[column_name].keys())
