from base_details_window import BaseDetailsWindow
from content import contents_complex_details
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from function import *
from styles import *


class DetailsComplexWindow(BaseDetailsWindow):
    def __init__(self, switch_view_callback, color_map):
        super().__init__("complex", switch_view_callback, contents_complex_details, color_map)
        self.weighted_edit_distance_widget = None

    def setup_options(self):
        super().setup_options()
        self.add_table_option()
        self.choice_option = self.add_choice_option("selected_evaluation_edit_distance",
                                                   ["edit_distance", "edit_distance_separate", "weighted_edit_distance"])
        self.choice_option.currentTextChanged.connect(self.on_evaluation_change)

    def add_table_option(self):
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Excluded Attributes'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("background-color: inherit;")
        self.load_excluded_attributes_into_table()

        add_button = QPushButton('Add')
        remove_button = QPushButton('Remove')
        text_color = get_contrasting_text_color(self.color_map.get('complex'))
        add_button.setStyleSheet(button_style % (text_color, text_color))
        remove_button.setStyleSheet(button_style % (text_color, text_color))
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
        attribute, ok = QInputDialog.getText(self, 'Add Attribute', 'Attribute name:')
        if ok and attribute:
            add_excluded_attribute(attribute)
            self.load_excluded_attributes_into_table()

    def remove_attribute(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            attribute = selected_items[0].text()
            remove_excluded_attribute(attribute)
            self.load_excluded_attributes_into_table()

    def on_evaluation_change(self, value):
        if value == "weighted_edit_distance":
            if not self.weighted_edit_distance_widget:
                self.weighted_edit_distance_widget = WeightedEditDistanceWidget()
                self.main_layout.addWidget(self.weighted_edit_distance_widget)
            self.weighted_edit_distance_widget.setVisible(True)
        else:
            if self.weighted_edit_distance_widget:
                self.weighted_edit_distance_widget.setVisible(False)


class WeightedEditDistanceWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.sliders_layout = QHBoxLayout()
        self.sliders = []
        self.percent_boxes = []
        self.weights = [33, 33, 34]  # Default values

        for i in range(3):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(self.weights[i])
            slider.valueChanged.connect(self.update_weights_from_sliders)

            percent_box = QSpinBox()
            percent_box.setRange(0, 100)
            percent_box.setValue(self.weights[i])
            percent_box.valueChanged.connect(self.update_weights_from_boxes)

            self.sliders.append(slider)
            self.percent_boxes.append(percent_box)

            self.sliders_layout.addWidget(slider)
            self.sliders_layout.addWidget(percent_box)

        self.layout.addLayout(self.sliders_layout)

    def update_weights_from_sliders(self):
        total_weight = sum(slider.value() for slider in self.sliders)
        for i in range(3):
            self.weights[i] = (self.sliders[i].value() * 100) // total_weight

        self.adjust_weights()
        self.update_boxes()

    def update_weights_from_boxes(self):
        total_weight = sum(box.value() for box in self.percent_boxes)
        for i in range(3):
            self.weights[i] = (self.percent_boxes[i].value() * 100) // total_weight

        self.adjust_weights()
        self.update_sliders()

    def adjust_weights(self):
        total = sum(self.weights)
        if total != 100:
            diff = 100 - total
            self.weights[2] += diff  # Adjust the last weight to ensure the sum is 100

    def update_sliders(self):
        for i in range(3):
            self.sliders[i].setValue(self.weights[i])

    def update_boxes(self):
        for i in range(3):
            self.percent_boxes[i].setValue(self.weights[i])
