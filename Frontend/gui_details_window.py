from function import save_type_encoding
from PySide6 import QtCore as Qt
from PySide6.QtWidgets import *
from styles import *
from content import contents_details
import subprocess

class DetailsWindow(QWidget):
    def __init__(self, main_window, encoding, switch_view_callback):
        super().__init__()
        self.main_window = main_window
        self.encoding = encoding
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        color = color_map.get(self.encoding, color_map.get("default"))
        self.setStyleSheet(f"background-color: {color};")

        self.title = QLabel(contents_details["window_title_details"].format(self.encoding.capitalize()))
        self.title.setAlignment(Qt.Qt.AlignCenter)
        self.title.setStyleSheet(title_label_style)
        self.title.setFixedHeight(40)

        description = QLabel("Detailed settings for " + self.encoding + " encoding")
        #description.setStyleSheet(contents_details["window_description_style"])

        self.back_button = QPushButton(contents_details["back_button"])
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(lambda: self.switch_view_callback("main"))

        self.next_button = QPushButton("Avanti")
        self.next_button.setStyleSheet(button_style)  # Assuming you have a global button style
        self.next_button.clicked.connect(self.on_next_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(description)
        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)

        self.setLayout(layout)
        self.setWindowTitle(contents_details["window_title_details"].format(self.encoding.capitalize()))

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def update_for_encoding(self, encoding):
        self.encoding = encoding
        # Update the UI components based on the new encoding
        self.setStyleSheet(f"background-color: {color_map[self.encoding]};")
        self.title.setText(contents_details["window_title_details"].format(self.encoding.capitalize()))
        # Update other UI components as necessary

    def on_next_clicked(self):
        # This method will be triggered when the "Next" button is clicked
        # Signal to switch to the RunWindow view
        self.switch_view_callback('run')
