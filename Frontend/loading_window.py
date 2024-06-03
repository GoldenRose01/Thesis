from PyQt6.QtCore import *
from PyQt6.QtSvgWidgets import *
from PyQt6.QtWidgets import *


class LoadingWindow(QWidget):
    def __init__(self, duration=5000):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        self.svg_widget = QSvgWidget("Frontend/svg/Sigillo_Università_di_Trento.svg")
        layout.addWidget(self.svg_widget)
        self.setLayout(layout)
        QTimer.singleShot(duration, self.close)