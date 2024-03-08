import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from gui_details_window import DetailsWindow
from content import contents_main as contents
from styles import *
from function import save_type_encoding

class MainWindow(QWidget):
    options_dat_path = "../Option.dat"

    def __init__(self, switch_view_callback):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: {color_map['default']}; {main_window_style}")
        layout = QVBoxLayout()

        title = QLabel(contents["title"])
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        description = QLabel(contents["description"])
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        for encoding in ["simple", "complex", "declarative"]:
            btn = QPushButton(contents[f"{encoding}_encoding"])
            btn.setStyleSheet(button_style)
            btn.clicked.connect(lambda checked, e=encoding: self.on_encoding_selected(e))
            layout.addWidget(btn)

        self.setLayout(layout)


    def on_encoding_selected(self, encoding):
        # Callback function to switch view to details or run window
        self.switch_view_callback(encoding)