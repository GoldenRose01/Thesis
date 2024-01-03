import pdb  # Importa il modulo pdb per il debug
import sys  # Importa il modulo sys per l'accesso alle variabili e ai puntatori

# Importa i moduli e le librerie necessarie
from src.dataset_manager import dataset_confs  # Importa le configurazioni dei dataset
import pandas as pd  # Importa la libreria pandas per la manipolazione dei dati
import numpy as np  # Importa la libreria numpy per operazioni numeriche
import os  # Importa il modulo os per l'accesso al sistema operativo
import matplotlib.pyplot as plt  # Importa il modulo matplotlib per la visualizzazione dei dati
from sklearn.model_selection import StratifiedKFold  # Importa StratifiedKFold per la divisione stratificata del dataset


# noinspection DuplicatedCode
class DatasetManager:

    def __init__(self, dataset_name):
        # Inizializza la classe DatasetManager con il nome del dataset
        self.dataset_name = dataset_name

        # Estrae le colonne chiave dalle configurazioni dei dataset
        self.case_id_col = dataset_confs.case_id_col[self.dataset_name]
        self.activity_col = dataset_confs.activity_col[self.dataset_name]
        self.timestamp_col = dataset_confs.timestamp_col[self.dataset_name]
        self.label_col = dataset_confs.label_col[self.dataset_name]
        self.pos_label = dataset_confs.pos_label[self.dataset_name]

        # Estrae le colonne categoriche dinamiche, statiche e le colonne numeriche dinamiche e statiche
        self.dynamic_cat_cols = dataset_confs.dynamic_cat_cols[self.dataset_name]
        self.static_cat_cols = dataset_confs.static_cat_cols[self.dataset_name]
        self.dynamic_num_cols = dataset_confs.dynamic_num_cols[self.dataset_name]
        self.static_num_cols = dataset_confs.static_num_cols[self.dataset_name]

        # Definisce le colonne per la classificazione temporale
        self.sorting_cols = [self.timestamp_col, self.activity_col]

    def read_dataset(self, dataset_path):
        # Legge il dataset dal percorso specificato
        # Configura i tipi di dati per le colonne
        dtypes = {col: "object" for col in
                  self.dynamic_cat_cols + self.static_cat_cols + [self.case_id_col, self.label_col, self.timestamp_col]}
        for col in self.dynamic_num_cols + self.static_num_cols:
            dtypes[col] = "float"

        # Legge il dataset CSV e converte la colonna del timestamp in un formato datetime
        data = pd.read_csv(os.path.join(dataset_path, dataset_confs.filename[self.dataset_name]), sep=";", dtype=dtypes)
        data[self.timestamp_col] = pd.to_datetime(data[self.timestamp_col])

        return data

    # noinspection DuplicatedCode
    def split_data(self, data, train_ratio, split="temporal", seed=22):
        # Divide il dataset in train e test utilizzando una divisione temporale o casuale

        grouped = data.groupby(self.case_id_col)
        start_timestamps = grouped[self.timestamp_col].min().reset_index()
        if split == "temporal":
            start_timestamps = start_timestamps.sort_values(self.timestamp_col, ascending=True, kind="mergesort")
        elif split == "random":
            np.random.seed(seed)
            start_timestamps = start_timestamps.reindex(np.random.permutation(start_timestamps.index))
        train_ids = list(start_timestamps[self.case_id_col])[:int(train_ratio * len(start_timestamps))]
        train = data[data[self.case_id_col].isin(train_ids)].sort_values(self.timestamp_col, ascending=True,
                                                                         kind='mergesort')
        test = data[~data[self.case_id_col].isin(train_ids)].sort_values(self.timestamp_col, ascending=True,
                                                                         kind='mergesort')
        return train, test

    def split_data_strict(self, data, train_ratio, split="temporal"):
        # Divide il dataset in train e test utilizzando una divisione temporale e scarta gli eventi che si sovrappongono

        data = data.sort_values(self.sorting_cols, ascending=True, kind='mergesort')
        grouped = data.groupby(self.case_id_col)
        start_timestamps = grouped[self.timestamp_col].min().reset_index()
        start_timestamps = start_timestamps.sort_values(self.timestamp_col, ascending=True, kind='mergesort')
        train_ids = list(start_timestamps[self.case_id_col])[:int(train_ratio * len(start_timestamps))]
        train = data[data[self.case_id_col].isin(train_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                         kind='mergesort')
        test = data[~data[self.case_id_col].isin(train_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                         kind='mergesort')
        split_ts = test[self.timestamp_col].min()
        train = train[train[self.timestamp_col] < split_ts]
        return train, test

    def split_data_discard(self, data, train_ratio, split="temporal"):
        # Divide il dataset in train e test utilizzando una divisione temporale e scarta gli eventi che si sovrappongono

        data = data.sort_values(self.sorting_cols, ascending=True, kind='mergesort')
        grouped = data.groupby(self.case_id_col)
        start_timestamps = grouped[self.timestamp_col].min().reset_index()
        start_timestamps = start_timestamps.sort_values(self.timestamp_col, ascending=True, kind='mergesort')
        train_ids = list(start_timestamps[self.case_id_col])[:int(train_ratio * len(start_timestamps))]
        train = data[data[self.case_id_col].isin(train_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                         kind='mergesort')
        test = data[~data[self.case_id_col].isin(train_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                         kind='mergesort')
        split_ts = test[self.timestamp_col].min()
        overlapping_cases = train[train[self.timestamp_col] >= split_ts][self.case_id_col].unique()
        train = train[~train[self.case_id_col].isin(overlapping_cases)]
        return (train, test)

    def split_val(self, data, val_ratio, split="random", seed=22):
        # Divide il dataset in train e validation utilizzando una divisione temporale o casuale

        grouped = data.groupby(self.case_id_col)
        start_timestamps = grouped[self.timestamp_col].min().reset_index()
        if split == "temporal":
            start_timestamps = start_timestamps.sort_values(self.timestamp_col, ascending=True, kind="mergesort")
        elif split == "random":
            np.random.seed(seed)
            start_timestamps = start_timestamps.reindex(np.random.permutation(start_timestamps.index))
        val_ids = list(start_timestamps[self.case_id_col])[-int(val_ratio * len(start_timestamps)):]
        val = data[data[self.case_id_col].isin(val_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                     kind="mergesort")
        train = data[~data[self.case_id_col].isin(val_ids)].sort_values(self.sorting_cols, ascending=True,
                                                                        kind="mergesort")
        return (train, val)

    def generate_prefix_data(self, data, min_length, max_length, gap=1):
        # Genera dati di prefisso (ogni prefisso possibile diventa una traccia)

        data['case_length'] = data.groupby(self.case_id_col)[self.activity_col].transform(len)

        dt_prefixes = data[data['case_length'] >= min_length].groupby(self.case_id_col).head(min_length)
        dt_prefixes["prefix_nr"] = 1
        dt_prefixes["orig_case_id"] = dt_prefixes[self.case_id_col]
        for nr_events in range(min_length + gap, max_length + 1, gap):
            tmp = data[data['case_length'] >= nr_events].groupby(self.case_id_col).head(nr_events)
            tmp["orig_case_id"] = tmp[self.case_id_col]
            tmp[self.case_id_col] = tmp[self.case_id_col].apply(lambda x: "%s_%s" % (x, nr_events))
            tmp["prefix_nr"] = nr_events
            dt_prefixes = pd.concat([dt_prefixes, tmp], axis=0)

        dt_prefixes['case_length'] = dt_prefixes['case_length'].apply(lambda x: min(max_length, x))
        return dt_prefixes

    def get_pos_case_length_quantile(self, data, quantile=0.90, save_hist=False, ):
        # Calcola la lunghezza dei casi positivi in base a un quantile specificato

        if save_hist:
            hist = data.groupby(self.case_id_col).size().plot.hist(bins=20)
            hist_1 = data[data[self.label_col] == self.pos_label].groupby(self.case_id_col).size().plot.hist(bins=20)
            plt.savefig(f'lbl_hist_{self.dataset_name}.pdf')
        return int(
            np.ceil(data[data[self.label_col] == self.pos_label].groupby(self.case_id_col).size().quantile(quantile)))

    def get_indexes(self, data):
        # Ottiene gli indici dei dati

        return data.groupby(self.case_id_col).first().index

    def get_relevant_data_by_indexes(self, data, indexes):
        # Ottiene i dati rilevanti in base agli indici specificati

        return data[data[self.case_id_col].isin(indexes)]

    def get_label(self, data):
        # Ottiene l'etichetta dei dati

        return data.groupby(self.case_id_col).first()[self.label_col]

    def get_prefix_lengths(self, data):
        # Ottiene le lunghezze dei prefissi

        return data.groupby(self.case_id_col).last()["prefix_nr"]

    def get_trace_attributes(self, data):

        # Ottiene gli attributi a livello di traccia
        return data[self.static_cat_cols + self.static_num_cols].drop_duplicates()

    def get_case_ids(self, data, nr_events=1):
        # Ottiene gli ID dei casi

        case_ids = pd.Series(data.groupby(self.case_id_col).first().index)
        if nr_events > 1:
            case_ids = case_ids.apply(lambda x: "_".join(x.split("_")[:-1]))
        return case_ids

    def get_resource_attributes(self, data):
        # Ottiene attributi specifici delle risorse
        # Richiede che il dataset abbia colonne identificate per le risorse
        resource_cols = [col for col in data.columns if 'resource' in col]
        return data[resource_cols]

    def get_label_numeric(self, data):
        # Ottiene l'etichetta numerica dei dati

        y = self.get_label(data)  # una riga per caso
        return [1 if label == self.pos_label else 0 for label in y]

    def get_class_ratio(self, data):
        # Ottiene il rapporto tra le classi dei dati

        class_freqs = data[self.label_col].value_counts()
        return class_freqs[self.pos_label] / class_freqs.sum()

    def get_stratified_split_generator(self, data, n_splits=5, shuffle=True, random_state=22):
        # Ottiene un generatore per la divisione stratificata dei dati

        grouped_firsts = data.groupby(self.case_id_col, as_index=False).first()
        skf = StratifiedKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

        for train_index, test_index in skf.split(grouped_firsts, grouped_firsts[self.label_col]):
            current_train_names = grouped_firsts[self.case_id_col][train_index]
            train_chunk = data[data[self.case_id_col].isin(current_train_names)].sort_values(self.timestamp_col,
                                                                                             ascending=True,
                                                                                             kind='mergesort')
            test_chunk = data[~data[self.case_id_col].isin(current_train_names)].sort_values(self.timestamp_col,
                                                                                             ascending=True,
                                                                                             kind='mergesort')
            yield (train_chunk, test_chunk)

    def get_idx_split_generator(self, dt_for_splitting, n_splits=5, shuffle=True, random_state=22):
        # Ottiene un generatore per la divisione degli indici dei dati

        skf = StratifiedKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

        for train_index, test_index in skf.split(dt_for_splitting, dt_for_splitting[self.label_col]):
            current_train_names = dt_for_splitting[self.case_id_col][train_index]
            current_test_names = dt_for_splitting[self.case_id_col][test_index]
            yield (current_train_names, current_test_names)
