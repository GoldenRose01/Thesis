from function import save_type_encoding
from PySide6 import QtCore as Qt
from PySide6.QtWidgets import *
from styles import *
from content import contents_details
from function import *
import subprocess
import os

class DetailsWindow(QWidget):
    def __init__(self,switch_view_callback,encoding):
        super().__init__()
        self.encoding=encoding
        self.switch_view_callback = switch_view_callback
        self.options = self.load_options()
        self.initUI()

    def set_encoding(self, encoding):
        self.encoding = encoding

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

        self.title = QLabel(contents_details["window_title_details"].format(self.encoding))
        self.title.setAlignment(Qt.Qt.AlignCenter)  # Corrected from previous feedback
        self.title.setStyleSheet(title_label_style)
        self.title.setFixedHeight(40)

        self.description = QLabel("Impostazioni dettagliate per il " + self.encoding + " encoding")
        self.description.setMinimumHeight(100)
        # Initialize the layout before setting up options
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.description)

        self.setup_options()

        self.back_button = QPushButton(contents_details["back_button"])
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(lambda: self.switch_view_callback("main"))

        self.next_button = QPushButton("Avanti")
        self.next_button.setStyleSheet(button_style)
        self.next_button.clicked.connect(self.on_next_clicked)

        self.main_layout.addWidget(self.back_button)
        self.main_layout.addWidget(self.next_button)

        self.setLayout(self.main_layout)
        self.setWindowTitle(contents_details["window_title_details"].format(self.encoding.capitalize()))

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

        #Per ogni tipo di encoding aggiungi le caratteristiche specifiche
        if self.encoding == "simple":
            #self.add_{tipo_di_impostazione}("{nome_dell'impostazione}", ["parametro1" ,"parametro2"])
            pass
        elif self.encoding == "complex":
            # self.add_{tipo_di_impostazione}("{nome_dell'impostazione}", ["parametro1" ,"parametro2"])
            self.add_table_option()
            self.add_choice_option("selected_evaluation_edit_distance", ["edit_distance", "edit_distance_separate", "weighted_edit_distance"])
            pass
        elif self.encoding == "declarative":
            # self.add_{tipo_di_impostazione}("{nome_dell'impostazione}", ["parametro1" ,"parametro2"])
            pass

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

    def add_table_option(self):
        # Gestione dell'opzione excluded_attributes per l'encoding complex
        self.table = QTableWidget()
        self.table.setColumnCount(1)  # Solo una colonna per gli attributi
        self.table.setHorizontalHeaderLabels(['Excluded Attributes'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.load_excluded_attributes_into_table()

        add_button = QPushButton('Add')
        remove_button = QPushButton('Remove')
        add_button.clicked.connect(self.add_attribute)
        remove_button.clicked.connect(self.remove_attribute)

        layout = QHBoxLayout()
        layout.addWidget(add_button)
        layout.addWidget(remove_button)

        self.main_layout.addWidget(self.table)
        self.main_layout.addLayout(layout)

    def load_excluded_attributes_into_table(self):
        attributes = self.options.get('excluded_attributes', '').split(';')
        self.table.setRowCount(len(attributes))
        for i, attribute in enumerate(attributes):
            self.table.setItem(i, 0, QTableWidgetItem(attribute))

    def add_attribute(self):
        # Logic to add an attribute
        attribute, ok = QInputDialog.getText(self, 'Add Attribute', 'Attribute name:')
        if ok and attribute:
            # Update the Option.dat file and the table
            add_excluded_attribute(attribute)  # Assumes this function is defined in function.py
            self.load_excluded_attributes_into_table()

    def remove_attribute(self):
        # Logic to remove a selected attribute
        selected_items = self.table.selectedItems()
        if selected_items:
            attribute = selected_items[0].text()
            remove_excluded_attribute(attribute)  # Assumes this function is defined in function.py
            self.load_excluded_attributes_into_table()

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def on_next_clicked(self):
        self.switch_view_callback('run')

    def update_option(self, option_name, value):
        self.options[option_name] = value
