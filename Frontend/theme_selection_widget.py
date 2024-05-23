# theme_selection_widget.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup

class ThemeSelectionWidget(QWidget):
    def __init__(self, theme_change_callback):
        super().__init__()
        self.theme_change_callback = theme_change_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        light_theme_radio = QRadioButton("Light Theme")
        dark_theme_radio = QRadioButton("Dark Theme")

        button_group = QButtonGroup(self)
        button_group.addButton(light_theme_radio)
        button_group.addButton(dark_theme_radio)

        light_theme_radio.setChecked(True)
        light_theme_radio.toggled.connect(lambda: self.theme_change_callback("light"))
        dark_theme_radio.toggled.connect(lambda: self.theme_change_callback("dark"))

        self.setLayout(layout)
        light_theme_radio.setParent(self)
        dark_theme_radio.setParent(self)
        light_theme_radio.setGeometry(10, 10, 200, 30)
        dark_theme_radio.setGeometry(10, 40, 200, 30)
