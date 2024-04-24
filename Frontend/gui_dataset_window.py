import os
from PySide6 import QtCore as Qt
from PySide6.QtWidgets import *
from function import *
from styles import *
from content import contents_run_window
import sys

class DatasetWindow(QWidget):
    def __init__(self, switch_view_callback):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: {color_map['default']};")
        layout = QVBoxLayout()

        title = QLabel("Run Encoding Process")
        title.setAlignment(Qt.Qt.AlignCenter)
        layout.addWidget(title)

        # Placeholder for file selection list or other content
        self.file_list = QListWidget()
        # Populate the list with files or options
        layout.addWidget(self.file_list)

        run_button = QPushButton('Run')
        run_button.setStyleSheet(button_style)
        run_button.clicked.connect(self.on_run_clicked)
        layout.addWidget(run_button)

        back_button = QPushButton('Indietro')
        back_button.setStyleSheet(button_style)
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def on_run_clicked(self):
        # Implement the logic to handle the run action
        print("Run process started...")

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def update_for_files(self, files):
        # Optional: Update the file list or other UI components based on current application state
        pass