from base_details_window import BaseDetailsWindow
from content import contents_complex_details
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QInputDialog
from function import add_excluded_attribute, remove_excluded_attribute

class DetailsComplexWindow(BaseDetailsWindow):
    def __init__(self, switch_view_callback):
        super().__init__("complex", switch_view_callback, contents_complex_details)

    def setup_options(self):
        super().setup_options()
        self.add_table_option()
        self.add_choice_option("selected_evaluation_edit_distance", ["edit_distance", "edit_distance_separate", "weighted_edit_distance"])

    def add_table_option(self):
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Excluded Attributes'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("background-color: inherit;")  # Ensure uniform color
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
