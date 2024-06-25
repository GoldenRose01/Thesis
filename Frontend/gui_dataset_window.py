import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QGridLayout
from PyQt6.QtGui import QIcon

from function import *
from styles import *
from content import contents_dataset_window

input_folder = os.path.join(os.getcwd(), '../media/input')


class DatasetWindow(QWidget):
    def __init__(self, switch_view_callback, color_map):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.selected_files = set()
        self.color_map = color_map
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: {self.color_map['default']};")
        self.layout = QVBoxLayout()

        self.title_label = QLabel("Run Encoding Process")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Descrizione della pagina
        self.description_label = QLabel(contents_dataset_window["dataset_page_description"])
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.description_label)

        # Collegamento per aprire la cartella
        folder_icon_path = 'svg/Folder.png'
        open_folder_button = QPushButton(QIcon(folder_icon_path), contents_dataset_window["open_folder_link_text"])
        open_folder_button.setStyleSheet(button_style)
        open_folder_button.clicked.connect(self.open_input_folder)
        self.layout.addWidget(open_folder_button)

        # Sezione per i file .csv con pulsante di ricarica
        self.files_layout = QGridLayout()
        self.load_files()
        self.layout.addLayout(self.files_layout)

        reload_button = QPushButton('↻')  # Pulsante di ricarica
        reload_button.setStyleSheet(button_style)
        reload_button.clicked.connect(self.load_files)
        self.layout.addWidget(reload_button, alignment=Qt.AlignmentFlag.AlignRight)

        run_button = QPushButton(contents_dataset_window["run_button_text"])
        run_button.setStyleSheet(button_style)
        run_button.clicked.connect(self.on_run_clicked)
        self.layout.addWidget(run_button)

        back_button = QPushButton('Indietro')
        back_button.setStyleSheet(button_style)
        back_button.clicked.connect(self.on_back_clicked)
        self.layout.addWidget(back_button)

        self.setLayout(self.layout)

    def load_files(self):
        # Clear existing buttons
        while self.files_layout.count():
            child = self.files_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Path relativo alla cartella media/input all'interno della cartella Frontend
        if os.path.exists(input_folder):
            files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
            row = 0
            col = 0
            for file in files:
                checkbox = QCheckBox(file.split('.')[0])  # Non rimuovere underscore
                checkbox.setStyleSheet(title_checkbox_style)
                checkbox.stateChanged.connect(lambda state, cb=checkbox: self.update_title_color(cb, cb.isChecked()))
                if file in self.selected_files:
                    checkbox.setChecked(True)
                self.update_title_color(checkbox, checkbox.isChecked())
                self.files_layout.addWidget(checkbox, row, col)
                col += 1
                if col > 2:  # Tre checkbox per riga
                    col = 0
                    row += 1

    def update_title_color(self, checkbox, is_checked):
        if is_checked:
            checkbox.setStyleSheet(
                f"QCheckBox {{ font-size: 14px; padding: 5px; spacing: 10px; color: {self.color_map['title_selected']}; }}")
            self.selected_files.add(checkbox.text() + '.csv')
        else:
            checkbox.setStyleSheet(
                f"QCheckBox {{ font-size: 14px; padding: 5px; spacing: 10px; color: {self.color_map['title_unselected']}; }}")
            self.selected_files.discard(checkbox.text() + '.csv')

    def on_run_clicked(self):
        # Save the selected file names to a .dat file
        with open('Datasets_names.dat', 'w') as f:
            for file in self.selected_files:
                f.write(file + '\n')
        print("Run process started")

    def on_back_clicked(self):
        # Signal to switch back to the main view or another appropriate view
        self.switch_view_callback('main')

    def open_input_folder(self):
        if sys.platform == "win32":
            os.startfile(input_folder)
        elif sys.platform == "darwin":
            os.system(f"open {input_folder}")
        else:
            os.system(f"xdg-open {input_folder}")

    def set_title(self, title):
        self.title_label.setText(title)

    def update_color_map(self, color_map):
        self.color_map = color_map
