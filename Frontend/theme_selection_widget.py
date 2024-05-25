from PyQt6.QtWidgets import QWidget, QVBoxLayout, QRadioButton
from PyQt6.QtCore import Qt

class ThemeSelectionWidget(QWidget):
    def __init__(self, set_theme_callback):
        super().__init__()
        self.set_theme_callback = set_theme_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        light_theme_radio = QRadioButton("Light Theme")
        dark_theme_radio = QRadioButton("Dark Theme")

        layout.addWidget(light_theme_radio)
        layout.addWidget(dark_theme_radio)

        self.setLayout(layout)
