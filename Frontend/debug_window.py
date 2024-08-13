import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, \
    QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DebugWindow(QMainWindow):
    def __init__(self, theme):
        super().__init__()
        self.setWindowTitle("Debug Window")
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

        self.boolean_options = []
        self.add_boolean_option("enable_log", "Enable Log")
        self.add_boolean_option("Allprint", "Allprint")
        self.add_boolean_option("eval_stamp", "Eval Stamp")
        self.add_boolean_option("recc_stamp", "Recc Stamp")
        self.add_boolean_option("print_length", "Print Length")
        self.add_boolean_option("print_log", "Print Log")
        self.add_boolean_option("Print_edit_distance", "Print Edit Distance")
        self.add_boolean_option("print_dt", "Print DT")

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
        self.forward_button.clicked.connect(self.go_to_dataset)
        self.nav_layout.addWidget(self.forward_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(self.nav_layout)

    def add_boolean_option(self, option_name, label_text):
        layout = QHBoxLayout()

        check_box = QCheckBox("")
        check_box.setChecked(option_name == "print_dt")  # preset attivo di default solo per print_dt
        check_box.setStyleSheet(f"QCheckBox {{color: {self.text_color};}}")
        check_box.toggled.connect(
            lambda checked, lbl=label_text, box=check_box: self.update_boolean_option(lbl, checked, box))

        option_label = QLabel(label_text)
        option_label.setFont(QFont("Arial", 14))
        option_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        option_label.setStyleSheet(f"color: {self.text_color}")

        layout.addWidget(check_box)
        layout.addWidget(option_label)
        layout.addStretch()
        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.main_layout.addWidget(container_widget)
        self.boolean_options.append((label_text, check_box))

        if option_name == "Allprint":
            check_box.toggled.connect(self.allprint_toggled)

    def update_boolean_option(self, label_text, checked, box):
        color = "green" if checked else "red"
        box.setStyleSheet(f"QCheckBox {{color: {self.text_color};}}")

    def allprint_toggled(self, checked):
        for label_text, check_box in self.boolean_options:
            if label_text in ["Eval Stamp", "Recc Stamp", "Print Length", "Print Log", "Print Edit Distance",
                              "Print DT"]:
                check_box.setChecked(checked)

    def save_options(self):
        options = {
            'enable_log': self.boolean_options[0][1].isChecked(),
            'Allprint': self.boolean_options[1][1].isChecked(),
            'eval_stamp': self.boolean_options[2][1].isChecked(),
            'recc_stamp': self.boolean_options[3][1].isChecked(),
            'print_length': self.boolean_options[4][1].isChecked(),
            'print_log': self.boolean_options[5][1].isChecked(),
            'Print_edit_distance': self.boolean_options[6][1].isChecked(),
            'print_dt': self.boolean_options[7][1].isChecked()
        }

        with open("Options.dat", "w") as f:
            for key, value in options.items():
                f.write(f"{key}={value}\n")

    def go_back(self):
        from encoding_window import EncodingWindow
        self.encoding_window = EncodingWindow()
        self.encoding_window.show()
        self.close()

    def go_to_dataset(self):
        self.save_options()
        from dataset_window import DatasetWindow
        self.dataset_window = DatasetWindow(self.theme)
        self.dataset_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugWindow("light")  # Usa "light" o "dark" a seconda del tema
    window.show()
    sys.exit(app.exec())
