from PyQt6.QtWidgets import *
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

class CustomSwitch(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.checkbox = QCheckBox(self)
        self.checkbox.setStyleSheet(self.getStylesheet())
        self.checkbox.setTristate(False)
        self.checkbox.setChecked(False)

        self.checkbox.stateChanged.connect(self.on_state_changed)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.checkbox)
        self.setLayout(layout)

    def on_state_changed(self, state):
        self.checkbox.setChecked(state == Qt.CheckState.Checked)

    def getStylesheet(self):
        return """
        QCheckBox::indicator {
            width: 3em;
            height: 1.5em;
            border-radius: 0.75em;
            background-color: hsl(210,90%,70%);
            position: relative;
        }
        QCheckBox::indicator:checked {
            background-color: hsl(290,90%,40%);
        }
        QCheckBox::indicator:unchecked {
            background-color: hsl(220,90%,40%);
        }
        QCheckBox::indicator::before {
            content: "";
            width: 1.25em;
            height: 1.25em;
            border-radius: 50%;
            background-color: hsl(0,0%,100%);
            position: absolute;
            top: 0.125em;
            left: 0.125em;
            transition: transform 0.3s cubic-bezier(0.76,0.05,0.24,0.95);
        }
        QCheckBox::indicator:checked::before {
            transform: translateX(1.5em);
            background-color: hsl(0,0%,0%);
        }
        """