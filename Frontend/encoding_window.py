import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
from content import contents_main
from styles import styles


class EncodingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(contents_main["window_title"])
        self.setGeometry(100, 100, 1440, 720)

        self.theme = "light"
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: white; color: black;")
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.header_layout = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout)

        # Increase font size for the labels
        label_font = QFont()
        label_font.setPointSize(label_font.pointSize() + 4)

        self.title_label = QLabel(contents_main["title"])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(label_font)
        self.main_layout.addWidget(self.title_label)

        self.description_label = QLabel(contents_main["description"])
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setFont(label_font)
        self.main_layout.addWidget(self.description_label)

        self.buttons = [
            (contents_main["simple_encoding"], self.show_simple_option, styles['simple']),
            (contents_main["complex_encoding"], self.show_complex_option, styles['complex']),
            (contents_main["declarative_encoding"], self.show_declarative_option, styles['declarative']),
        ]

        button_layout = QVBoxLayout()
        button_font = QFont()
        button_font.setPointSize(button_font.pointSize() + 4)
        button_height = (0.66 * 720) // 3  # 66% of screen height divided by 3 buttons

        for text, callback, color in self.buttons:
            button = QPushButton(text)
            button.setFont(button_font)
            button.setStyleSheet(f"background-color: {color}; color: black;")
            button.setFixedHeight(button_height)
            button.clicked.connect(callback)
            button_layout.addWidget(button)

        self.main_layout.addLayout(button_layout)

        # Add theme switch button
        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(50, 50)
        self.update_theme_button()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.header_layout.addWidget(self.theme_button, alignment=Qt.AlignRight)

    def update_theme_button(self):
        icon = "Frontend/svg/sun.svg" if self.theme == "dark" else "Frontend/svg/moon.svg"
        self.theme_button.setIcon(QIcon(icon))
        self.theme_button.setIconSize(self.theme_button.size())

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            self.central_widget.setStyleSheet("background-color: white; color: black;")
        else:
            self.theme = "dark"
            self.central_widget.setStyleSheet("background-color: black; color: white;")
        self.update_theme_button()

    def show_simple_option(self):
        from simple_option import Simpleencoding
        self.option_window = Simpleencoding()
        self.option_window.show()
        self.close()

    def show_complex_option(self):
        from complex_option import Complexencoding
        self.option_window = Complexencoding()
        self.option_window.show()
        self.close()

    def show_declarative_option(self):
        from declarative_option import DeclarativeOptionWindow
        self.option_window = DeclarativeOptionWindow()
        self.option_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EncodingWindow()
    window.show()
    sys.exit(app.exec())
