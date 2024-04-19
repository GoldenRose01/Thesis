import sys
from PySide6.QtCore import Qt, QRect, QCoreApplication
from PySide6.QtWidgets import *
from gui_details_window import DetailsWindow
from content import contents_main as contents
from styles import *
from function import save_type_encoding

class MainWindow(QWidget):
    options_dat_path = "../Option.dat"

    def __init__(self,encoding,switch_view_callback):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        self.setWindowTitle(contents["window_title"])
        self.setStyleSheet(f"background-color: {color_map['default']}; {main_window_style}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        description = QLabel(contents["description"])
        description.setAlignment(Qt.AlignCenter)
        description.setMinimumHeight(200)
        layout.addWidget(description)

        simple_button = QPushButton(contents["simple_encoding"])
        complex_button = QPushButton(contents["complex_encoding"])
        declarative_button = QPushButton(contents["declarative_encoding"])

        # Set specific colors for buttons based on the type
        simple_button.setStyleSheet(f"background-color: {color_map['simple']}; {button_style}")
        complex_button.setStyleSheet(f"background-color: {color_map['complex']}; {button_style}")
        declarative_button.setStyleSheet(f"background-color: {color_map['declarative']}; {button_style}")

        # Impostare la politica di dimensionamento per espansione
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        simple_button.setSizePolicy(policy)
        complex_button.setSizePolicy(policy)
        declarative_button.setSizePolicy(policy)

        # Impostazione di dimensioni minime
        simple_button.setMinimumHeight(100)
        complex_button.setMinimumHeight(100)
        declarative_button.setMinimumHeight(100)

        simple_button.clicked.connect(lambda: self.on_button_clicked("simple"))
        complex_button.clicked.connect(lambda: self.on_button_clicked("complex"))
        declarative_button.clicked.connect(lambda: self.on_button_clicked("declarative"))

        layout.addWidget(simple_button, 1)
        layout.addWidget(complex_button, 1)
        layout.addWidget(declarative_button, 1)

        self.setLayout(layout)
        self.center_window()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_button_clicked(self, encoding):
        try:
            self.selected_encoding = encoding
            self.switch_view_callback(encoding)
        except Exception as e:
            print(f"Error: {e}")