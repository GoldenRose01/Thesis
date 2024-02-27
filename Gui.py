import sys
import subprocess
from PySide6 import QtCore, QtWidgets, QtGui

# Finestra principale
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Imposta titolo e dimensione finestra
        self.setWindowTitle("Outcome-based Prescriptive Monitoring di Processi di Business con control e data flow")
        self.setGeometry(300, 300, 800, 300)

        # Crea layout
        layout = QtWidgets.QVBoxLayout()

        # Crea titolo
        title = QtWidgets.QLabel("Scegli un metodo di encoding:")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Crea pulsanti
        self.simple_button = QtWidgets.QPushButton("Simple encoding")
        self.complex_button = QtWidgets.QPushButton("Complex encoding")
        self.declarative_button = QtWidgets.QPushButton("Declarative encoding")

        # Imposta stile dei pulsanti
        self.simple_button.setStyleSheet("QPushButton { width: 300px; height: 50px; }")
        self.complex_button.setStyleSheet("QPushButton { width: 300px; height: 50px; }")
        self.declarative_button.setStyleSheet("QPushButton { width: 300px; height: 50px; }")

        # Aggiunge pulsanti al layout
        layout.addWidget(self.simple_button)
        layout.addWidget(self.complex_button)
        layout.addWidget(self.declarative_button)

        # Crea widget centrale e imposta layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Collega azioni ai pulsanti
        self.simple_button.clicked.connect(self.show_simple_page)
        self.complex_button.clicked.connect(self.show_complex_page)
        self.declarative_button.clicked.connect(self.show_declarative_page)

    # Mostra pagina per "Simple encoding"
    def show_simple_page(self):
        print("Simple encoding selected")

    # Mostra pagina per "Complex encoding"
    def show_complex_page(self):
        print("Complex encoding selected")

    # Mostra pagina per "Declarative encoding"
    def show_declarative_page(self):
        print("Declarative encoding selected")

class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self, encoding_type):
        super().__init__()
        self.setWindowTitle("Dettagli Encoding")
        self.setGeometry(300, 300, 800, 600)
        self.initUI(encoding_type)

        # Crea layout a due colonne
        layout = QtWidgets.QHBoxLayout()

        # Crea widget a sinistra con le scelte
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()
        self.buttons = []

        simple_button = QtWidgets.QPushButton("Simple encoding")
        simple_button.setStyleSheet("QPushButton { background-color: #6CA0DC; }")
        simple_button.clicked.connect(lambda: self.on_button_clicked(simple_button))
        left_layout.addWidget(simple_button)
        self.buttons.append(simple_button)

        complex_button = QtWidgets.QPushButton("Complex encoding")
        complex_button.setStyleSheet("QPushButton { background-color: #4CAF50; }")
        complex_button.clicked.connect(lambda: self.on_button_clicked(complex_button))
        left_layout.addWidget(complex_button)
        self.buttons.append(complex_button)

        declarative_button = QtWidgets.QPushButton("Declarative encoding")
        declarative_button.setStyleSheet("QPushButton { background-color: #FFC107; }")
        declarative_button.clicked.connect(lambda: self.on_button_clicked(declarative_button))
        left_layout.addWidget(declarative_button)
        self.buttons.append(declarative_button)

        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        # Crea widget a destra con le opzioni
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.encoding_widgets = {}

        self.encoding_widgets["simple"] = self.create_simple_widget()
        self.encoding_widgets["complex"] = self.create_complex_widget()
        self.encoding_widgets["declarative"] = self.create_declarative_widget()

        layout.addWidget(self.stacked_widget)

        # Crea widget centrale e imposta layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_simple_widget(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("Threshold:"))
        self.threshold_slider = QtWidgets.QSlider(QtCore.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(120)
        self.threshold_slider.setValue(1)
        self.threshold_slider.valueChanged.connect(lambda value: self.update_setting("Threshold", value * 0.0125))
        layout.addWidget(self.threshold_slider)

        btn_minus = QtWidgets.QPushButton("-")
        btn_plus = QtWidgets.QPushButton("+")
        btn_minus.clicked.connect(lambda: self.adjust_t_threshold(-1))
        btn_plus.clicked.connect(lambda: self.adjust_threshold(1))
        layout.addWidget(btn_minus)
        layout.addWidget(btn_plus)

        options = ["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"]

        for option in options: checkbox = QtWidgets.QCheckBox(option)
        checkbox.stateChanged.connect(lambda state, x=option: self.update_setting(x, state == QtCore.Qt.Checked))
        layout.addWidget(checkbox)

        settings_widget = QtWidgets.QWidget()
        settings_widget.setLayout(layout)
        return settings_widget

    def create_complex_widget(self):
        layout = QtWidgets.QVBoxLayout()

        options = ["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"]

        for option in options: checkbox = QtWidgets.QCheckBox(option)
        checkbox.stateChanged.connect(lambda state, x=option: self.update_setting(x, state == QtCore.Qt.Checked))
        layout.addWidget(checkbox)

        settings_widget = QtWidgets.QWidget()
        settings_widget.setLayout(layout)
        return settings_widget

    def create_declarative_widget(self):
        layout = QtWidgets.QVBoxLayout()

        options = ["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain", "One_hot_encoding",
            "Use_score"]

        for option in options: checkbox = QtWidgets.QCheckBox(option)
        checkbox.stateChanged.connect(lambda state, x=option: self.update_setting(x, state == QtCore.Qt.Checked))
        layout.addWidget(checkbox)

        settings_widget = QtWidgets.QWidget()
        settings_widget.setLayout(layout)
        return settings_widget

    def on_button_clicked(self, selected_button):
        encoding_type = selected_button.text().lower()

        self.update_setting("EncodingType", encoding_type)
        self.stacked_widget.setCurrentWidget(self.encoding_widgets[encoding_type])
        self.update_button_styles(selected_button)

    def update_button_styles(self, active_button):
        for button in self.buttons:
            if button == active_button:
            # Preserva lo stile di background corrente del pulsante attivo
            # Assumendo che lo stile di background sia definito correttamente
                current_style = button.styleSheet()
                background_style = current_style.split('background-color:')[1].split(';')[
                    0] if 'background-color:' in current_style else 'none'
                button.setStyleSheet(
                                f"QPushButton {{ background-color: {background_style}; border-radius: 20px; padding: 10px; font-size: 16pt; }}")
                else
                button.setStyleSheet("QPushButton { border-radius: 20px; padding: 10px; font-size: 16pt; }")
# Esegui applicazione
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1080)
        self.setMinimumHeight(720)
        self.settings = {}
        self.init_ui()
        self.load_settings()
        self.init_stacked_widget()

    def init_ui(self):
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        #self.central_widget.setStyleSheet("background-color: black;")

        self.btn_simple = QPushButton('Simple Encoding')
        self.btn_complex = QPushButton('Complex Encoding')
        self.btn_declarative = QPushButton('Declarative Encoding')
        self.buttons = [self.btn_simple, self.btn_complex, self.btn_declarative]

        self.btn_simple.setStyleSheet("background-color: purple;")
        self.btn_complex.setStyleSheet("background-color: blue;")
        self.btn_declarative.setStyleSheet("background-color: yellow;")

        for button in self.buttons:
            button.clicked.connect(lambda _, b=button: self.on_button_clicked(b))

        button_layout = QVBoxLayout()
        for button in self.buttons:
            button_layout.addWidget(button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.main_layout.addWidget(button_widget)

        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.show_confirm_dialog)
        button_layout.addWidget(self.run_button)

    def load_settings(self):
        try:
            with open("Settings.txt", "r") as file:
                for line in file:
                    setting, value = line.strip().split(": ")
                    self.settings[setting] = value
        except FileNotFoundError:
            pass

    def init_stacked_widget(self):
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        self.encoding_widgets = {
            "complex": self.create_settings_widget("complex"),
            "simple": self.create_settings_widget("simple"),
            "declarative": self.create_settings_widget("declarative")
        }
        for widget in self.encoding_widgets.values():
            self.stacked_widget.addWidget(widget)

    def create_settings_widget(self, encoding_type):
        layout = QVBoxLayout()
        settings_widget = QWidget()

        if encoding_type != "declarative":
            layout.addWidget(QLabel("Threshold:"))
            self.threshold_slider = QSlider(Qt.Horizontal)
            self.threshold_slider.setMinimum(0)
            self.threshold_slider.setMaximum(120)
            self.threshold_slider.setValue(1)
            self.threshold_slider.valueChanged.connect(lambda value: self.update_setting("Threshold", value * 0.0125))
            layout.addWidget(self.threshold_slider)

            btn_minus = QPushButton("-")
            btn_plus = QPushButton("+")
            btn_minus.clicked.connect(lambda: self.adjust_threshold(-1))
            btn_plus.clicked.connect(lambda: self.adjust_threshold(1))
            layout.addWidget(btn_minus)
            layout.addWidget(btn_plus)

        options = ["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"]

        if encoding_type == "declarative":
            options += ["One_hot_encoding", "Use_score"]

        for option in options:
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(lambda state, x=option: self.update_setting(x, state == Qt.Checked))
            layout.addWidget(checkbox)

        settings_widget.setLayout(layout)
        return settings_widget

    def adjust_threshold(self, delta):
        self.threshold_slider.setValue(self.threshold_slider.value() + delta)
        self.update_setting("Threshold", self.threshold_slider.value() * 0.0125)

    def update_setting(self, setting, value):
        self.settings[setting] = value

    def on_button_clicked(self, selected_button):
        encoding_type = selected_button.text().lower()
        self.update_setting("EncodingType", encoding_type)
        self.stacked_widget.setCurrentWidget(self.encoding_widgets[encoding_type])
        self.update_button_styles(selected_button)

    def update_button_styles(self, active_button):
        for button in self.buttons:
            if button == active_button:
                button.setStyleSheet(f"QPushButton {{ background-color: {button.color}; }}")
            else:
                button.setStyleSheet(
                    QPushButton {
                        border-radius: 20px;
                        padding: 10px;
                        font-size: 16pt;
                    }
                )

    def show_confirm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Confermare i settaggi")

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        settings_text = self.get_settings_text()
        text_edit.setHtml(settings_text)

        yes_button = QPushButton("Sì")
        yes_button.clicked.connect(lambda: self.confirm_and_run(dialog))
        no_button = QPushButton("No")
        no_button.clicked.connect(dialog.close)

        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_and_run(self, dialog):
        self.save_settings()
        dialog.close()
        self.run_experiment()

    def get_settings_text(self):
        settings_text = ""
        with open("Settings.txt", "r") as file:
            for line in file:
                setting, value = line.strip().split(": ")
                color = "green" if value.lower() == "true" else "red"
                settings_text += f'<p><span style="color:{color};">{setting}: {value}</span></p>'
        return settings_text

    def save_settings(self):
        with open("Settings.txt", "w") as file:
            for setting, value in self.settings.items():
                file.write(f"{setting}: {value}\n")

    def run_experiment(self):
        subprocess.run(["python", "Run_experiment.py"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
"""