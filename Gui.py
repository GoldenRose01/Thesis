import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                               QWidget, QStackedWidget, QListWidget, QCheckBox,
                               QSlider, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1080)  # Imposta la larghezza minima della finestra
        self.setMinimumHeight(720)
        self.settings = {}  # Dizionario per mantenere i settaggi
        self.init_ui()
        self.load_settings()  # Carica i settaggi da Settings.txt


    def init_ui(self):
        # Layout principale
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.central_widget.setStyleSheet("background-color: black;")

        # Bottoni per i diversi tipi di encoding
        self.btn_simple = QPushButton('Simple Encoding')
        self.btn_complex = QPushButton('Complex Encoding')
        self.btn_declarative = QPushButton('Declarative Encoding')
        self.buttons = [self.btn_simple, self.btn_complex, self.btn_declarative]

        # Imposta i colori iniziali dei bottoni
        self.btn_simple.setStyleSheet("background-color: purple;")
        self.btn_complex.setStyleSheet("background-color: blue;")
        self.btn_declarative.setStyleSheet("background-color: yellow;")

        # Collega i bottoni alle funzioni
        for button in self.buttons:
            button.clicked.connect(lambda _, b=button: self.on_button_clicked(b))

        # Layout per i bottoni
        button_layout = QVBoxLayout()
        for button in self.buttons:
            button_layout.addWidget(button)

        # Widget per i bottoni
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.main_layout.addWidget(button_widget)

    def load_settings(self):
        try:
            with open("Settings.txt", "r") as file:
                for line in file:
                    setting, value = line.strip().split(": ")
                    self.settings[setting] = value
        except FileNotFoundError:
            pass

    def init_stacked_widget(self):
        # Aggiungi i widget per ogni tipo di encoding
        self.stacked_widget.addWidget(self.create_settings_widget("complex"))
        self.stacked_widget.addWidget(self.create_settings_widget("simple"))
        self.stacked_widget.addWidget(self.create_settings_widget("declarative"))

    def create_settings_widget(self, encoding_type):
        # Crea un widget per le impostazioni specifiche di ogni encoding
        layout = QVBoxLayout()
        settings_widget = QWidget()

        # Slider e bottoni per Threshold
        if encoding_type != "declarative":  # Aggiungi solo per simple e complex
            layout.addWidget(QLabel("Threshold:"))
            self.threshold_slider = QSlider(Qt.Horizontal)
            self.threshold_slider.setMinimum(0)
            self.threshold_slider.setMaximum(120)  # 1.5/0.0125 = 120 steps
            self.threshold_slider.setValue(1)  # Valore iniziale
            self.threshold_slider.valueChanged.connect(lambda value: self.update_setting("Threshold", value * 0.0125))
            layout.addWidget(self.threshold_slider)

            # Bottoni per incrementare/diminuire il valore di Threshold
            btn_minus = QPushButton("-")
            btn_plus = QPushButton("+")
            btn_minus.clicked.connect(lambda: self.adjust_threshold(-1))
            btn_plus.clicked.connect(lambda: self.adjust_threshold(1))
            layout.addWidget(btn_minus)
            layout.addWidget(btn_plus)

        # Opzioni comuni
        options = ["Optimize_dt", "Print_dt", "Reranking", "Sat_type", "Compute_gain"]

        # Opzioni aggiuntive per declarative
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

    def update_setting(self, setting, value):
        self.settings[setting] = value
        self.save_settings()

    def save_settings(self):
        with open("Settings.txt", "w") as file:
            for setting, value in self.settings.items():
                file.write(f"{setting}: {value}\n")

    def on_button_clicked(self, selected_button):
        for button in self.buttons:
            button.setStyleSheet("")
        # Imposta il colore dello sfondo
        if selected_button == self.btn_simple:
            self.central_widget.setStyleSheet("background-color: purple;")
            selected_button.setStyleSheet("QPushButton { background-color: purple; }")
        elif selected_button == self.btn_complex:
            self.central_widget.setStyleSheet("background-color: blue;")
            selected_button.setStyleSheet("QPushButton { background-color: blue; }")
        elif selected_button == self.btn_declarative:
            self.central_widget.setStyleSheet("background-color: yellow;")
            selected_button.setStyleSheet("QPushButton { background-color: yellow; }")

        # Aggiorna l'area centrale con i widget di impostazione
        self.main_layout.takeAt(1)  # Rimuove il widget precedente
        index = self.buttons.index(selected_button)
        settings_widget = self.create_settings_widget(["complex", "simple", "declarative"][index])
        self.main_layout.addWidget(settings_widget)
        self.update_setting("EncodingType", selected_button.text())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

"""import tkinter as tk
from tkinter import ttk

def open_settings(encoding_type):
    settings_window = tk.Toplevel(root)
    settings_window.title(f"{encoding_type} Settings")
    settings_window.configure(bg='black')
    # Add the settings widgets to 'settings_window' instead of 'root'
    # ... Rest of your settings window code ...

def create_main_window():
    main_window = tk.Tk()
    main_window.title("Encoding Selection")
    main_window.geometry('800x500')

    simplex_button = tk.Button(main_window, text="Simplex Encoding", command=lambda: open_settings("Simplex"))
    simplex_button.pack(pady=10)

    complex_button = tk.Button(main_window, text="Complex Encoding", command=lambda: open_settings("Complex"))
    complex_button.pack(pady=10)

    main_window.mainloop()

# Call the function to create and show the main window
create_main_window()

def run_settings():
     print("Settings Run")
    # Add code to handle the settings here

def create_rounded_button(parent, width, height, text, command):
    frame = tk.Frame(parent, bg='black')
    canvas = tk.Canvas(frame, width=width, height=height, bg='black', highlightthickness=0)
    canvas.pack(side='left')

    # Create rounded corners
    rad = 10  # Radius of the corners
    canvas.create_arc((2, 2, 2*rad, 2*rad), start=90, extent=90, fill='black')
    canvas.create_arc((width-2*rad, 2, width-2, 2*rad), start=0, extent=90, fill='black')
    canvas.create_arc((width-2*rad, height-2*rad, width-2, height-2), start=270, extent=90, fill='black')
    canvas.create_arc((2, height-2*rad, 2*rad, height-2), start=180, extent=90, fill='black')
    canvas.create_rectangle(rad, 2, width-rad, height-2, fill='black', outline='black')
    canvas.create_rectangle(2, rad, width-2, height-rad, fill='black', outline='black')

    # Label as the button
    label = tk.Label(frame, text=text, fg='white', bg='black')
    label.pack(fill='both', expand=True)
    label.bind('<Button-1>', lambda e: command())

    return frame

def update_bool_setting(setting):
    settings[setting] = not settings[setting]
    update_buttons()

def update_buttons():
    for setting, frame in toggle_buttons.items():
        label = frame.winfo_children()[1]  # Label is the second child
        label.config(bg='green' if settings[setting] else 'red')

def arrange_widgets():
    column_count = 2  # Set the number of columns
    row, col = 0, 0
    for widget in all_widgets:
        widget.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
        col += 1
        if col >= column_count:
            col = 0
            row += 1
    # Place the RUN button
    run_button.grid(row=row, column=0, columnspan=column_count, padx=10, pady=10, sticky='ew')

# Create the main window
root = tk.Tk()
root.title("Settings")
root.configure(bg='black')
root.geometry('500x600')  # Initial window size

# Define settings
settings = {
    'reranking': False,
    'cumulative_res': False,  # Ensure this key is included
    'optimize_dt': True,
    'print_dt': True,
    'compute_gain': False,
    'smooth_factor': 1,
    'train_prefix_log': False,
    'one_hot_encoding': False,
    'use_score': True,
    'compute_baseline': False,
    'sat_type': 'count_occurrences',  # Include this if used in the GUI
    'fitness_type': 'mean',  # Include this if used in the GUI
    # Add any other settings that are used in the GUI
}

# Create toggle buttons and other widgets
toggle_buttons = {}
all_widgets = []
for setting in ['reranking', 'cumulative_res', 'optimize_dt', 'print_dt', 'compute_gain', 'train_prefix_log', 'one_hot_encoding', 'use_score', 'compute_baseline']:
    button_frame = create_rounded_button(root, 100, 30, setting, lambda s=setting: update_bool_setting(s))
    toggle_buttons[setting] = button_frame
    all_widgets.append(button_frame)

sat_type_var = tk.StringVar(value=settings['sat_type'])
sat_type_dropdown = ttk.Combobox(root, textvariable=sat_type_var, values=['count_occurrences', 'count_activations', 'strong'])
all_widgets.append(sat_type_dropdown)

smooth_factor_var = tk.DoubleVar(value=settings.get('smooth_factor', 1))
smooth_factor_slider = tk.Scale(root, from_=0, to=5, resolution=0.25, orient='horizontal', variable=smooth_factor_var)
all_widgets.append(smooth_factor_slider)

# Run Button
run_button = tk.Button(root, text="RUN", command=run_settings)
all_widgets.append(run_button)

# Arrange widgets and update button states
arrange_widgets()
update_buttons()

root.mainloop()
"""