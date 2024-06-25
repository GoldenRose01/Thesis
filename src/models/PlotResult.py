import matplotlib.pyplot as plt
import os
import settings

class PlotResult:

    def __init__(self, dict_results, prefix_lenght_list, folder):
        # Inizializzazione dell'oggetto PlotResult
        # dict_results: un dizionario contenente i risultati
        # prefix_lenght_list: una lista delle lunghezze dei prefissi
        # folder: la cartella in cui salvare i grafici generati
        self.dict_results = dict_results
        self.folder = folder
        self.prefix_lenght_list = prefix_lenght_list

    def toPng(self, metric, title):
        # Metodo per generare un grafico in formato PNG
        plt.clf()
        if metric == "prec-rec":
            # Impostazione dell'asse x come "Precision" e dell'asse y come "Recall" se la metrica è "prec-rec"
            plt.xlabel('Precision', fontsize=18)
            plt.ylabel('Recall', fontsize=18)
            prec = [getattr(res_obj, "precision") for res_obj in self.dict_results]
            rec = [getattr(res_obj, "recall") for res_obj in self.dict_results]
            plt.plot(rec, prec, color=settings.method_color, label='Precision-Recall')
        else:
            # Impostazione dell'asse x come "Prefix length" e dell'asse y come la metrica specificata
            plt.xlabel('Prefix length', fontsize=18)
            plt.ylabel(metric, fontsize=18)
            result_list = [getattr(res_obj, metric) for res_obj in self.dict_results]
            plt.plot(self.prefix_lenght_list, result_list, color=settings.method_color)
            if metric == "gain":
                # Aggiunge una linea tratteggiata orizzontale a y=1 se la metrica è "gain"
                plt.axhline(y=1, color='k', linestyle='--', label='Gain')

        plt.legend(title, fontsize=14)
        plt.tight_layout()  # Imposta il layout del grafico
        plt.savefig(os.path.join(self.folder, f'{title}.pdf'))  # Salva il grafico come file PDF
