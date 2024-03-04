import sys
import subprocess
from PySide6 import QtCore, QtWidgets

# Definizione della mappa dei colori per sfondi e pulsanti
color_map = {
    "simple": "#ADD8E6",
    "complex": "#FFD700",
    "declarative": "#90EE90"
}

class DetailsWindow(QtWidgets.QWidget):
    def __init__(self, switch_function, settings):
        super().__init__()
        self.setGeometry(300, 300, 1080, 720)
        self.switch_function = switch_function
        self.settings = settings
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Titolo della finestra
        self.title = QtWidgets.QLabel("Dettagli Encoding")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Area per le impostazioni specifiche
        self.settings_area = QtWidgets.QVBoxLayout()

    def update_settings_area(self, encoding_type):
        # Pulisci l'area delle impostazioni
        while self.settings_area.count():
            child = self.settings_area.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Aggiorna il titolo e lo sfondo
        self.title.setText(f"Dettagli Encoding - {encoding_type.capitalize()}")
        self.setStyleSheet(f"background-color: {color_map[encoding_type]};")

        # Aggiungi widget specifici in base al tipo di encoding
        if encoding_type == "complex":
            label = QtWidgets.QLabel("Excluded Attributes:")
            self.settings_area.addWidget(label)
            excluded_edit = QtWidgets.QLineEdit(", ".join(self.settings.get("excluded_attributes", [])))
            self.settings_area.addWidget(excluded_edit)
            self.settings['excluded_edit'] = excluded_edit

        # Aggiungi altri controlli per simple e declarative come necessario

    def save_settings_and_run(self, encoding_type):
        if encoding_type == "complex":
            excluded_attrs = self.settings['excluded_edit'].text().split(', ')
            self.settings["excluded_attributes"] = excluded_attrs

        # Salva le impostazioni in options.dat
        with open("options.dat", "w") as f:
            for key, value in self.settings.items():
                if key != 'excluded_edit':  # Salta i widget QLineEdit
                    if isinstance(value, list):
                        f.write(f"{key} = {value}\n")
                    else:
                        f.write(f"{key} = {value}\n")

        # Avvia run_experiment.py
        subprocess.run(["python", "run_experiment.py"], check=True)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outcome-based Prescriptive Monitoring di Processi di Business")
        self.setGeometry(300, 300, 1080, 720)
        self.settings = self.load_settings()
        self.details_window = DetailsWindow(self.show_details_window, self.settings)
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout)

        title = QtWidgets.QLabel("Scegli un metodo di encoding:")
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title)

        # Pulsanti per le scelte
        choices_layout = QtWidgets.QHBoxLayout()
        for encoding in ["simple", "complex", "declarative"]:
            btn = QtWidgets.QPushButton(f"{encoding.capitalize()} encoding")
            btn.setStyleSheet(f"QPushButton {{ background-color: {color_map[encoding]}; }}")
            btn.clicked.connect(lambda _, e=encoding: self.show_details_window(e))
            choices_layout.addWidget(btn)

        run_button = QtWidgets.QPushButton("Run")
        run_button.clicked.connect(lambda: self.details_window.save_settings_and_run(self.details_window.encoding_type))
        choices_layout.addWidget(run_button)

        self.layout.addLayout(choices_layout)

        # Area di visualizzazione delle impostazioni
        self.details_area = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.details_area)
        self.details_area.addWidget(self.details_window)

    def load_settings(self):
        settings = {}
        try:
            with open("options.dat", "r") as f:
                for line in f:
                    key, val = line.strip().split(' = ')
                    if key == "excluded_attributes":
                        settings[key] = val.strip('[]').replace("'", "").split(', ')
                    else:
                        settings[key] = val
        except FileNotFoundError:
            print("File options.dat non trovato. Utilizzo impostazioni predefinite.")
        return settings

    def show_details_window(self, encoding_type):
        self.details_window.encoding_type = encoding_type
        self.details_window.update_settings_area(encoding_type)
        self.details_window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
