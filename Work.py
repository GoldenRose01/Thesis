#da inserire in dataset_manager.py

def split_dataset(self, dataset_path):
    # Leggi il dataset utilizzando la funzione read_dataset
    data = self.read_dataset(dataset_path)

    # Estrai gli attributi categorici e numerici
    cat_attrs = self.static_cat_cols + self.dynamic_cat_cols
    num_attrs = self.static_num_cols + self.dynamic_num_cols

    # Crea una copia del dataset suddiviso
    data_cat = data[cat_attrs].copy()
    data_num = data[num_attrs].copy()

    # Ora puoi utilizzare data_cat e data_num per encoding o altre operazioni
    return data_cat, data_num



#per chiamare la funzione
"""

data_cat, data_num = data_manager.split_dataset("percorso_del_tuo_dataset.csv")

"""
#portare dove necessario data_cat e data_num per encoding e altro