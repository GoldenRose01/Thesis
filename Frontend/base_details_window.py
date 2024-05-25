from PyQt6 import QtCore as Qt
from PyQt6.QtWidgets import *
from styles import *
from function import *
import os

class BaseDetailsWindow(QWidget):
    def __init__(self, encoding, switch_view_callback, content_details, color_map):
        super().__init__()
        self.encoding = encoding
        self.switch_view_callback = switch_view_callback
        self.content_details = content_details
        self.options = self.load_options()
        self.color_map = color_map
        self.initUI()

    def update_color_map(self, new_color_map):
        self.color_map = new_color_map
        self.update_styles()

    def load_options(self):
        options = {}
        with open('Option.dat', 'r') as file:
            for line in file.readlines():
                key, value = line.strip().split('=')
                options[key.strip()] = value.strip()
        return options

    def initUI(self):
        color = self.color_map.get(self.encoding, self.color_map.get("default"))
        text_color = get_contrasting_text_color(color)
        self.setStyleSheet(f"background-color: {color};")

        self.title = QLabel(self.content_details["window_title_details"])
        self.title.setAlignment(Qt.Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(title_label_style % text_color)
        self.title.setFixedHeight(40)

        self.description = QLabel(f"Impostazioni dettagliate per il {self.encoding} encoding")
        self.description.setMinimumHeight(40)
        self.description.setStyleSheet(description_label_style % text_color)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setAlignment(Qt.Qt.AlignmentFlag.AlignTop)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.description)

        self.setup_options()

        self.back_button = QPushButton(self.content_details["back_button"])
        self.back_button.setStyleSheet(button_style % (text_color, text_color))
        self.back_button.clicked.connect(lambda: self.switch_view_callback("main"))

        self.next_button = QPushButton("Avanti")
        self.next_button.setStyleSheet(button_style % (text_color, text_color))
        self.next_button.clicked.connect(self.on_next_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.next_button)

        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle(self.content_details["window_title_details"])

    def setup_options(self):
        self.add_boolean_option("optimize_dt" )
        self.add_boolean_option("print_dt")
        self.add_boolean_option("Print_edit_distance")
        self.add_boolean_option("train_prefix_log")
        self.add_boolean_option("one_hot_encoding")
        self.add_boolean_option("use_score")
        self.add_boolean_option("print_log")
        self.add_boolean_option("print_length")
        self.add_numeric_option("sat_threshold", 0, 1, 0.05)
        self.add_choice_option("fitness_type", ["mean", "wmean"])

    def add_boolean_option(self, option_name):
        checkbox = QCheckBox(option_name.replace('_', ' ').capitalize())
        checkbox.setChecked(self.options.get(option_name) == 'True')
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
        layout = QHBoxLayout()
        label = QLabel(option_name.replace('_', ' ').capitalize())
        combobox = QComboBox()
        combobox.addItems(choices)
        current_value = self.options.get(option_name, choices[0])
        combobox.setCurrentText(current_value)
        combobox.currentTextChanged.connect(lambda value, name=option_name: self.update_option(name, value))
        layout.addWidget(label)
        layout.addWidget(combobox)
        self.main_layout.addLayout(layout)

    def on_next_clicked(self):
        self.switch_view_callback('dataset')

    def update_option(self, option_name, value):
        self.options[option_name] = value
