import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, \
    QPushButton, QScrollArea, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DatasetWindow(QMainWindow):
    def __init__(self, theme):
        super().__init__()
        self.setWindowTitle("Dataset Window")
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

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.header_layout = QHBoxLayout()
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(50, 50)
        self.refresh_button.clicked.connect(self.refresh_dataset_list)
        self.open_folder_button = QPushButton("📁")
        self.open_folder_button.setFixedSize(50, 50)
        self.open_folder_button.clicked.connect(self.open_input_folder)
        self.header_label = QLabel("Ricerca dei dataset in Media/input")
        self.header_label.setFont(QFont("Arial", 16))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet(f"color: {self.text_color}")
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addWidget(self.refresh_button)
        self.header_layout.addWidget(self.open_folder_button)

        self.main_layout.addLayout(self.header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.dataset_widget = QWidget()
        self.dataset_layout = QVBoxLayout()
        self.dataset_widget.setLayout(self.dataset_layout)
        self.scroll_area.setWidget(self.dataset_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.load_datasets()

        self.weighted_prefix_generation_checkbox = QCheckBox("Weighted Prefix Generation")
        self.weighted_prefix_generation_checkbox.setStyleSheet(f"color: {self.text_color}")
        self.main_layout.addWidget(self.weighted_prefix_generation_checkbox, alignment=Qt.AlignBottom)

        self.nav_layout = QHBoxLayout()

        # Add back button to bottom left
        self.back_button = QPushButton("Indietro")
        self.back_button.setFixedSize(100, 50)
        self.back_button.setStyleSheet(f"color: {self.text_color};")
        self.back_button.clicked.connect(self.go_back)
        self.nav_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        # Add forward button to bottom right
        self.forward_button = QPushButton("Avanti")
        self.forward_button.setFixedSize(100, 50)
        self.forward_button.setStyleSheet(f"color: {self.text_color};")
        self.forward_button.clicked.connect(self.go_to_terminal)
        self.nav_layout.addWidget(self.forward_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(self.nav_layout)

    def load_datasets(self):
        self.dataset_layout.setParent(None)
        self.dataset_layout = QVBoxLayout()
        self.dataset_widget.setLayout(self.dataset_layout)

        self.dataset_checkboxes = []
        input_folder = "media/input"
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)

        for filename in os.listdir(input_folder):
            if filename.endswith(".csv"):
                checkbox = QCheckBox(os.path.splitext(filename)[0])
                checkbox.setStyleSheet(f"color: {self.text_color}")
                self.dataset_checkboxes.append(checkbox)
                self.dataset_layout.addWidget(checkbox)

    def refresh_dataset_list(self):
        self.load_datasets()

    def open_input_folder(self):
        folder = os.path.abspath("media/input")
        if os.name == "nt":
            os.startfile(folder)
        elif os.name == "posix":
            subprocess.call(["xdg-open", folder])

    def save_options(self):
        selected_datasets = [checkbox.text() for checkbox in self.dataset_checkboxes if checkbox.isChecked()]
        with open("Datasets_names.dat", "w") as f:
            for dataset in selected_datasets:
                f.write(f"{dataset}\n")

        weighted_prefix_generation = self.weighted_prefix_generation_checkbox.isChecked()
        with open("option.dat", "a") as f:
            f.write(f"weighted_prefix_generation={weighted_prefix_generation}\n")

    def go_back(self):
        from debug_window import DebugWindow
        self.debug_window = DebugWindow(self.theme)
        self.debug_window.show()
        self.close()

    def go_to_terminal(self):
        self.save_options()
        from terminal_window import TerminalWindow
        self.terminal_window = TerminalWindow(self.theme)
        self.terminal_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatasetWindow("light")  # Usa "light" o "dark" a seconda del tema
    window.show()
    sys.exit(app.exec())
