from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from styles import *
from content import contents_main


class MainWindow(QWidget):
    options_dat_path = "Option.dat"

    def __init__(self, switch_view_callback, color_map):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.color_map = color_map
        self.initUI()

    def initUI(self):
        color = self.color_map['default']
        text_color = get_contrasting_text_color(color)
        self.setWindowTitle(contents_main["window_title"])
        self.setStyleSheet(f"background-color: {color}; {main_window_style % color}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(contents_main["description"])
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setMinimumHeight(100)
        layout.addWidget(description)

        simple_button = QPushButton(contents_main["simple_encoding"])
        complex_button = QPushButton(contents_main["complex_encoding"])
        declarative_button = QPushButton(contents_main["declarative_encoding"])

        # Set specific colors for buttons based on the type
        simple_button.setStyleSheet(
            f"background-color: {self.color_map['simple']}; {button_style % (text_color, text_color)}")
        complex_button.setStyleSheet(
            f"background-color: {self.color_map['complex']}; {button_style % (text_color, text_color)}")
        declarative_button.setStyleSheet(
            f"background-color: {self.color_map['declarative']}; {button_style % (text_color, text_color)}")

        # Set the size policy to expanding
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        simple_button.setSizePolicy(policy)
        complex_button.setSizePolicy(policy)
        declarative_button.setSizePolicy(policy)

        # Set minimum height for buttons
        simple_button.setMinimumHeight(100)
        complex_button.setMinimumHeight(100)
        declarative_button.setMinimumHeight(100)

        simple_button.clicked.connect(lambda: self.on_button_clicked("simple"))
        complex_button.clicked.connect(lambda: self.on_button_clicked("complex"))
        declarative_button.clicked.connect(lambda: self.on_button_clicked("declarative"))

        layout.addWidget(simple_button, 1)
        layout.addWidget(complex_button, 1)
        layout.addWidget(declarative_button, 1)

        self.switch_layout = QHBoxLayout()
        self.switch_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.theme_switch_button = QPushButton()
        self.update_theme_icon()
        self.theme_switch_button.setFixedSize(40, 40)
        self.theme_switch_button.clicked.connect(self.toggle_theme)

        self.switch_layout.addWidget(self.theme_switch_button)
        layout.addLayout(self.switch_layout)

        self.setLayout(layout)
        self.center_window()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_button_clicked(self, encoding):
        try:
            self.switch_view_callback(encoding)
        except Exception as e:
            print(f"Error: {e}")

    def toggle_theme(self):
        if self.color_map == color_map_light:
            self.color_map = color_map_dark
        else:
            self.color_map = color_map_light
        self.update_color_map(self.color_map)
        self.switch_view_callback('update_theme')
        self.update_theme_icon()

    def update_color_map(self, new_color_map):
        self.color_map = new_color_map
        self.initUI()

    def update_theme_icon(self):
        if self.color_map == color_map_light:
            icon = QIcon("svg/sun.svg")
        else:
            icon = QIcon("svg/moon.svg")
        self.theme_switch_button.setIcon(icon)
        self.theme_switch_button.setIconSize(QSize(30, 30))
