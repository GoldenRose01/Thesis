import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont


class TerminalWindow(QMainWindow):
    def __init__(self, theme):
        super().__init__()
        self.setWindowTitle("Terminal Window")
        self.setGeometry(100, 100, 1440, 720)

        self.theme = theme

        self.central_widget = QWidget()
        if theme == "dark":
            self.central_widget.setStyleSheet("background-color: black; color: white;")
            self.text_color = "white"
        else:
            self.central_widget.setStyleSheet("background-color: white; color: black;")
            self.text_color = "black"
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Courier", 10))
        self.layout.addWidget(self.terminal_output)

        self.nav_layout = QHBoxLayout()

        # Add stop button to bottom left
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(100, 50)
        self.stop_button.setStyleSheet(f"color: {self.text_color};")
        self.stop_button.clicked.connect(self.stop_process)
        self.nav_layout.addWidget(self.stop_button, alignment=Qt.AlignLeft)

        self.layout.addLayout(self.nav_layout)

        self.process = QProcess(self)
        self.process.setProgram("python")
        self.process.setArguments(["main.py"])
        self.process.setWorkingDirectory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.started.connect(self.process_started)
        self.process.finished.connect(self.process_finished)
        self.process.start()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.terminal_output.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.terminal_output.append(data)

    def process_started(self):
        self.terminal_output.append("Process started...\n")

    def process_finished(self):
        self.terminal_output.append("Process finished.\n")

    def stop_process(self):
        self.process.terminate()
        self.process.waitForFinished()
        self.go_back_to_encoding()

    def go_back_to_encoding(self):
        from encoding_window import EncodingWindow
        self.encoding_window = EncodingWindow()
        self.encoding_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalWindow("light")  # Usa "light" o "dark" a seconda del tema
    window.show()
    sys.exit(app.exec())
