import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont

class DeclarativeOptionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Declarative Option")
        self.setGeometry(100, 100, 1440, 720)

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: lightgray;")
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("This is the declarative option window.")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Add forward button to bottom right
        self.forward_button = QPushButton("Avanti")
        self.forward_button.setFixedSize(100, 50)
        self.forward_button.setStyleSheet("color: black;")
        self.forward_button.clicked.connect(self.go_to_debug)
        self.layout.addWidget(self.forward_button, alignment=Qt.AlignRight)

    def go_to_debug(self):
        # Passare alla finestra debug_window
        from debug_window import DebugWindow
        self.debug_window = DebugWindow()
        self.debug_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeclarativeOptionWindow()
    window.show()
    sys.exit(app.exec())
