from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from styles import *
from content import contents_terminal_window


class TerminalWindow(QWidget):
    def __init__(self, switch_view_callback):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel(contents_terminal_window["terminal_title"])
        title.setAlignment(Qt.AlignCenter)
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
        #self.next_button.setOpacity(0.5)  # Make it semi-transparent (need to adjust style)
        # Assuming next step is to switch to another view
        # self.next_button.clicked.connect(lambda: self.switch_view_callback('next_view_name'))
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def enable_next_button(self):
        self.next_button.setEnabled(True)
        self.next_button.setOpacity(1.0)  # Make it fully opaque
