import sys
from PySide6 import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, encoding_type="simple"):
        super().__init__()
        encoding_type = sys.argv[1] if len(sys.argv) > 1 else "simple"
        self.initUI(encoding_type)
        self.setWindowTitle("Dettagli Encoding")  # Imposta il titolo della finestra
        self.setGeometry(300, 300, 800, 600)  # Imposta la dimensione e la posizione della finestra
        self.settings = {}  # Inizializza un dizionario per memorizzare le impostazioni selezionate
        self.checkboxes = []  # Lista per tenere traccia dei checkbox

    def initUI(self, encoding_type):
        layout = QtWidgets.QHBoxLayout()  # Layout orizzontale per contenere widget laterali e centrali
        self.left_widget = QtWidgets.QWidget()  # Widget contenitore per i pulsanti laterali
        left_layout = QtWidgets.QVBoxLayout()  # Layout verticale per i pulsanti

        self.buttons = []  # Lista per tenere traccia dei pulsanti di encoding
        # Informazioni sui pulsanti: nome, colore e descrizione per il tooltip
        button_info = [
            ("Simple encoding", "#6CA0DC", "Descrizione base"),
            ("Complex encoding", "#4CAF50", "Descrizione base"),
            ("Declarative encoding", "#FFC107", "Descrizione base")
        ]

        # Crea i pulsanti in base alle informazioni fornite
        for name, color, tooltip in button_info:
            button = QtWidgets.QPushButton(name)
            button.setStyleSheet(f"QPushButton {{ background-color: {color}; border-radius: 20px; padding: 10px; }}")
            button.setToolTip(tooltip)  # Imposta il tooltip
            button.clicked.connect(self.make_button_handler(name))
            left_layout.addWidget(button)
            self.buttons.append(button)

        self.left_widget.setLayout(left_layout)
        layout.addWidget(self.left_widget)

        self.stacked_widget = QtWidgets.QStackedWidget()  # Widget per contenere diversi widget di encoding
        # Dizionario dei widget di encoding
        self.encoding_widgets = {
            "simple": self.create_simple_widget(),
            "complex": self.create_complex_widget(),
            "declarative": self.create_declarative_widget()
        }

        # Aggiunge i widget di encoding allo stacked_widget
        for widget in self.encoding_widgets.values():
            self.stacked_widget.addWidget(widget)

        layout.addWidget(self.stacked_widget)

        # Pulsante RUN in basso a destra per mostrare le impostazioni selezionate
        run_button = QtWidgets.QPushButton("RUN")
        run_button.clicked.connect(self.show_confirmation)
        run_layout = QtWidgets.QVBoxLayout()
        run_layout.addWidget(run_button, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        layout.addLayout(run_layout)

        # Imposta il widget centrale della QMainWindow
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Imposta il widget iniziale in base al tipo di encoding
        self.set_initial_widget(encoding_type)

    # Genera un gestore per ogni pulsante di encoding
    def make_button_handler(self, name):
        def handler():
            self.reset_settings()  # Resetta le impostazioni ogni volta che viene premuto un pulsante
            encoding_type = name.lower().replace(" encoding", "")
            self.update_setting("EncodingType", encoding_type)
            self.stacked_widget.setCurrentWidget(self.encoding_widgets[encoding_type])
            self.update_background_color(encoding_type)  # Aggiorna il colore di sfondo
        return handler

    # Mostra una finestra di dialogo con le impostazioni selezionate
    def show_confirmation(self):
        details = "\n".join([f"{key}: {value}" for key, value in self.settings.items()])
        QtWidgets.QMessageBox.information(self, "Confirmation Settings", f"Selected Details:\n{details}")

    # Crea widget di encoding semplice
    def create_simple_widget(self):
        return self.create_settings_widget(["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"])

    # Crea widget di encoding complesso
    def create_complex_widget(self):
        return self.create_settings_widget(["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"])

    # Crea widget di encoding dichiarativo
    def create_declarative_widget(self):
        return self.create_settings_widget(["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain", "One_hot_encoding", "Use_score"])

    # Crea un widget di impostazioni con checkbox
    def create_settings_widget(self, options):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        for option in options:
            checkbox = QtWidgets.QCheckBox(option)
            checkbox.stateChanged.connect(lambda state, x=option: self.update_setting(x, state == QtCore.Qt.Checked))
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)  # Aggiunge il checkbox alla lista per il tracking
        widget.setLayout(layout)
        return widget

    # Aggiorna le impostazioni selezionate
    def update_setting(self, setting, value):
        self.settings[setting] = value
        print(f"Setting: {setting}, Value: {value}")

    # Aggiorna il colore di sfondo in base al tipo di encoding selezionato
    def update_background_color(self, encoding_type):
        color_map = {
            "simple": "#CC7722",  # Ocra
            "complex": "#FFA500",  # Arancione
            "declarative": "#960018"  # Carmine
        }
        color = color_map.get(encoding_type, "#FFFFFF")  # Bianco se non trovato
        self.centralWidget().setStyleSheet(f"QWidget {{ background-color: {color}; }}")

    # Resetta tutte le impostazioni deselezionando i checkbox
    def reset_settings(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    # Imposta il widget iniziale in base al tipo di encoding
    def set_initial_widget(self, encoding_type):
        for button in self.buttons:
            if button.text().lower() == f"{encoding_type} encoding":
                self.make_button_handler(button.text())()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
