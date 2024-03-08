from function import save_type_encoding
from PySide6 import QtCore as Qt
from PySide6.QtWidgets import *
from styles import *
from content import contents_details
import subprocess

class DetailsWindow(QWidget):
    def __init__(self, encoding, switch_view_callback):
        super().__init__()
        self.encoding = encoding
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: {color_map[self.encoding]};")
        layout = QVBoxLayout()

        title = QLabel(contents_details["window_title_details"].format(self.encoding.capitalize()))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Example content, replace with actual content for your details view
        description = QLabel("Detailed settings for " + self.encoding + " encoding")
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        back_button = QPushButton('Indietro')
        back_button.setStyleSheet(button_style)
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def update_for_encoding(self, encoding):
        self.encoding = encoding
        # Update the UI components based on the new encoding
        self.setStyleSheet(f"background-color: {color_map[self.encoding]};")
        self.title.setText(contents_details["window_title_details"].format(self.encoding.capitalize()))
        # Update other UI components as necessary
