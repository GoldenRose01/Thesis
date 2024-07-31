from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from styles import *
from content import contents_terminal_window

class TerminalWindow(QWidget):
    def __init__(self, switch_view_callback, color_map):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.color_map = color_map
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel(contents_terminal_window["terminal_title"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Terminal output placeholder
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        layout.addWidget(self.terminal_output)

        # Back button
        self.back_button = QPushButton("Indietro")
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(lambda: self.switch_view_callback('run'))
        layout.addWidget(self.back_button)

        # Next button
        self.next_button = QPushButton("Prossimo")
        self.next_button.setStyleSheet(button_style)
        self.next_button.setEnabled(False)  # Initially disabled
        # Assuming next step is to switch to another view
        # self.next_button.clicked.connect(lambda: self.switch_view_callback('next_view_name'))
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def enable_next_button(self):
        self.next_button.setEnabled(True)

    def update_color_map(self, new_color_map):
       self.color_map = new_color_map
       self.initUI()
