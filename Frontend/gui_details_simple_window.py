from function import save_type_encoding
from PySide6 import QtCore as Qt
from PySide6.QtWidgets import *
from styles import *
from content import contents_simple_details
from function import *
import subprocess
import os

class DetailsSimpleWindow(QWidget):
    def __init__(self,switch_view_callback):
        super().__init__()
        self.encoding="simple"
        self.switch_view_callback = switch_view_callback
        self.options = self.load_options()
        self.initUI()

    def load_options(self):
        options = {}
        with open('../Option.dat', 'r') as file:
            for line in file.readlines():
                key, value = line.strip().split('=')
                options[key.strip()] = value.strip()
        return options

    def initUI(self):
        color = color_map.get(self.encoding, color_map.get("default"))
        self.setStyleSheet(f"background-color: {color};")

        self.title = QLabel(contents_simple_details["window_title_details"])
        self.title.setAlignment(Qt.Qt.AlignCenter)  # Corrected from previous feedback
        self.title.setStyleSheet(title_label_style)
        self.title.setFixedHeight(40)

        self.description = QLabel("Impostazioni dettagliate per il simple encoding")
        self.description.setMinimumHeight(100)
        # Initialize the layout before setting up options
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.description)

        self.setup_options()

        self.back_button = QPushButton(contents_simple_details["back_button"])
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(lambda: self.switch_view_callback("main"))

        self.next_button = QPushButton("Avanti")
        self.next_button.setStyleSheet(button_style)
        self.next_button.clicked.connect(self.on_next_clicked)

        self.main_layout.addWidget(self.back_button)
        self.main_layout.addWidget(self.next_button)

        self.setLayout(self.main_layout)
        self.setWindowTitle(contents_simple_details["window_title_details"])

    def setup_options(self):

        self.add_boolean_option("optimize_dt")
        self.add_boolean_option("print_dt")
        self.add_boolean_option("Print_edit_distance")
        self.add_boolean_option("train_prefix_log")
        self.add_boolean_option("one_hot_encoding")
        self.add_boolean_option("use_score")
        self.add_boolean_option("print_log")
        self.add_boolean_option("print_length")
        self.add_numeric_option("sat_threshold", 0, 1, 0.05)
        self.add_choice_option("fitness_type", ["mean", "wmean"])
        #self.add_{tipo_di_impostazione}("{nome_dell'impostazione}", ["parametro1" ,"parametro2"])


    def add_boolean_option(self, option_name):
        checkbox = QCheckBox(option_name.replace('_', ' ').capitalize())
        checkbox.setChecked(self.options[option_name] == 'True')
        checkbox.stateChanged.connect(lambda state, name=option_name: self.update_option(name, state))
        self.main_layout.addWidget(checkbox)

    def add_numeric_option(self, option_name, min_value, max_value, step):
        layout = QHBoxLayout()
        label = QLabel(option_name.replace('_', ' ').capitalize())
        spinBox = QDoubleSpinBox()
        spinBox.setMinimum(min_value)
        spinBox.setMaximum(max_value)
        spinBox.setSingleStep(step)
        current_value = float(self.options.get(option_name, min_value))
        spinBox.setValue(current_value)
        spinBox.valueChanged.connect(lambda value, name=option_name: self.update_option(name, str(value)))
        layout.addWidget(label)
        layout.addWidget(spinBox)
        self.main_layout.addLayout(layout)

    def add_choice_option(self, option_name, choices):
        combobox = QComboBox()
        combobox.addItems(choices)
        current_value = self.options[option_name]
        if current_value in choices:
            combobox.setCurrentText(current_value)
        combobox.currentTextChanged.connect(lambda value, name=option_name: self.update_option(name, value))
        self.main_layout.addWidget(combobox)

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def on_next_clicked(self):
        self.switch_view_callback('dataset')

    def update_option(self, option_name, value):
        self.options[option_name] = value
