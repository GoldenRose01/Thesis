import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QSlider, QRadioButton, QButtonGroup, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont
from content import contents_simple_details
from styles import styles

# Presettaggi
preset_options = {
    'sat_threshold': 0.75,
    'optimize_dt': True,
    'train_prefix_log': False,
    'one_hot_encoding': False,
    'use_score': True,
    'fitness_type': 'mean'
}


class Simpleencoding(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(contents_simple_details["window_title_details"])
        self.setGeometry(100, 100, 1440, 720)

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"background-color: {styles['simple']}")
        self.setCentralWidget(self.central_widget)

        self.main_layout = QGridLayout()
        self.central_widget.setLayout(self.main_layout)

        # Add back button to top left
        self.back_button = QPushButton(contents_simple_details["back_button"])
        self.back_button.setFixedSize(100, 50)
        self.back_button.setStyleSheet("color: black;")
        self.back_button.clicked.connect(self.go_back)
        self.main_layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignLeft)

        # Add forward button to bottom right
        self.forward_button = QPushButton(contents_simple_details["forward_button"])
        self.forward_button.setFixedSize(100, 50)
        self.forward_button.setStyleSheet("color: black;")
        self.forward_button.clicked.connect(self.save_options)
        self.main_layout.addWidget(self.forward_button, 10, 2, alignment=Qt.AlignRight)

        # Add boolean options
        self.boolean_options = []
        self.add_boolean_option("optimize_dt", contents_simple_details["optimize_dt"], 1, 0,
                                preset_options['optimize_dt'])
        self.add_boolean_option("train_prefix_log", contents_simple_details["train_prefix_log"], 2, 0,
                                preset_options['train_prefix_log'])
        self.add_boolean_option("one_hot_encoding", contents_simple_details["one_hot_encoding"], 3, 0,
                                preset_options['one_hot_encoding'])
        self.add_boolean_option("use_score", contents_simple_details["use_score"], 4, 0, preset_options['use_score'])

        # Add numeric option
        self.add_numeric_option("sat_threshold", contents_simple_details["sat_threshold"], 5, 0, 0, 1, 0.05,
                                preset_options['sat_threshold'])

        # Add choice option
        self.add_choice_option("fitness_type", contents_simple_details["fitness_type"], 6, 0, ["mean", "wmean"],
                               preset_options['fitness_type'])

    def add_boolean_option(self, option_name, label_text, row, col, preset_value):
        layout = QHBoxLayout()

        check_box = QPushButton("")
        check_box.setCheckable(True)
        check_box.setFixedSize(20, 20)
        check_box.setChecked(preset_value)
        check_box.setStyleSheet("QPushButton {background-color: white; border: 1px solid black; color: black;}")
        check_box.toggled.connect(
            lambda checked, lbl=label_text, box=check_box: self.update_boolean_option(lbl, checked, box))

        option_label = QLabel(label_text)
        option_label.setFont(QFont("Arial", 14))
        option_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        option_label.setStyleSheet("color: black")

        layout.addWidget(check_box)
        layout.addWidget(option_label)
        layout.addStretch()
        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.main_layout.addWidget(container_widget, row, col, 1, 3)
        self.boolean_options.append((option_label, check_box))

        # Update label initially based on preset value
        self.update_boolean_option(label_text, preset_value, check_box)

    def update_boolean_option(self, label_text, checked, box):
        for label, check_box in self.boolean_options:
            if check_box == box:
                if checked:
                    label.setText(f"{label_text} (True)")
                    label.setStyleSheet("color: green")
                else:
                    label.setText(f"{label_text} (False)")
                    label.setStyleSheet("color: red")

    def add_numeric_option(self, option_name, label_text, row, col, min_val, max_val, step, preset_value):
        layout = QVBoxLayout()

        self.slider_layout = QHBoxLayout()
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Arial", 14))
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: black")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val * 100))
        self.slider.setMaximum(int(max_val * 100))
        self.slider.setSingleStep(int(step * 100))
        self.slider.setValue(int(preset_value * 100))
        self.slider.valueChanged.connect(self.update_slider_label)

        self.slider_value_label = QLabel(f"{preset_value:.2f}")
        self.slider_value_label.setFont(QFont("Arial", 14))
        self.slider_value_label.setAlignment(Qt.AlignLeft)
        self.slider_value_label.setStyleSheet("color: black")

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)
        self.plus_button.setStyleSheet("color: black;")
        self.plus_button.clicked.connect(lambda: self.adjust_slider_value(self.slider, step))

        self.minus_button = QPushButton("-")
        self.minus_button.setFixedSize(30, 30)
        self.minus_button.setStyleSheet("color: black;")
        self.minus_button.clicked.connect(lambda: self.adjust_slider_value(self.slider, -step))

        self.slider_layout.addWidget(self.minus_button)
        self.slider_layout.addWidget(self.slider)
        self.slider_layout.addWidget(self.plus_button)

        layout.addWidget(self.label)
        layout.addWidget(self.slider_value_label)
        layout.addLayout(self.slider_layout)
        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.main_layout.addWidget(container_widget, row, col, 1, 3)

    def update_slider_label(self, value):
        self.slider_value_label.setText(f"{value / 100:.2f}")

    def adjust_slider_value(self, slider, step):
        current_value = slider.value()
        new_value = current_value + int(step * 100)
        slider.setValue(new_value)

    def add_choice_option(self, option_name, label_text, row, col, choices, preset_value):
        layout = QHBoxLayout()
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Arial", 14))
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: black")

        self.choice_layout = QVBoxLayout()
        self.button_group = QButtonGroup()

        for choice in choices:
            radio_button = QRadioButton(choice)
            radio_button.setFont(QFont("Arial", 14))
            radio_button.setStyleSheet("color: black")
            if choice == preset_value:
                radio_button.setChecked(True)
            self.button_group.addButton(radio_button)
            self.choice_layout.addWidget(radio_button)

        layout.addWidget(self.label)
        layout.addLayout(self.choice_layout)
        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.main_layout.addWidget(container_widget, row, col, 1, 3)

    def save_options(self):
        import sys
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
            QSlider, QRadioButton, QButtonGroup, QGridLayout
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor, QPalette, QFont
        from content import contents_simple_details
        from styles import styles

        # Presettaggi
        preset_options = {
            'sat_threshold': 0.75,
            'optimize_dt': True,
            'train_prefix_log': False,
            'one_hot_encoding': False,
            'use_score': True,
            'fitness_type': 'mean'
        }

        class Option1Window(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle(contents_simple_details["window_title_details"])
                self.setGeometry(100, 100, 1440, 720)

                self.central_widget = QWidget()
                self.central_widget.setStyleSheet(f"background-color: {styles['simple']}")
                self.setCentralWidget(self.central_widget)

                self.main_layout = QGridLayout()
                self.central_widget.setLayout(self.main_layout)

                # Add back button to top left
                self.back_button = QPushButton(contents_simple_details["back_button"])
                self.back_button.setFixedSize(100, 50)
                self.back_button.setStyleSheet("color: black;")
                self.back_button.clicked.connect(self.go_back)
                self.main_layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignLeft)

                # Add forward button to bottom right
                self.forward_button = QPushButton(contents_simple_details["forward_button"])
                self.forward_button.setFixedSize(100, 50)
                self.forward_button.setStyleSheet("color: black;")
                self.forward_button.clicked.connect(self.save_options)
                self.main_layout.addWidget(self.forward_button, 10, 2, alignment=Qt.AlignRight)

                # Add boolean options
                self.boolean_options = []
                self.add_boolean_option("optimize_dt", contents_simple_details["optimize_dt"], 1, 0,
                                        preset_options['optimize_dt'])
                self.add_boolean_option("train_prefix_log", contents_simple_details["train_prefix_log"], 2, 0,
                                        preset_options['train_prefix_log'])
                self.add_boolean_option("one_hot_encoding", contents_simple_details["one_hot_encoding"], 3, 0,
                                        preset_options['one_hot_encoding'])
                self.add_boolean_option("use_score", contents_simple_details["use_score"], 4, 0,
                                        preset_options['use_score'])

                # Add numeric option
                self.add_numeric_option("sat_threshold", contents_simple_details["sat_threshold"], 5, 0, 0, 1, 0.05,
                                        preset_options['sat_threshold'])

                # Add choice option
                self.add_choice_option("fitness_type", contents_simple_details["fitness_type"], 6, 0, ["mean", "wmean"],
                                       preset_options['fitness_type'])

            def add_boolean_option(self, option_name, label_text, row, col, preset_value):
                layout = QHBoxLayout()

                check_box = QPushButton("")
                check_box.setCheckable(True)
                check_box.setFixedSize(20, 20)
                check_box.setChecked(preset_value)
                check_box.setStyleSheet("QPushButton {background-color: white; border: 1px solid black; color: black;}")
                check_box.toggled.connect(
                    lambda checked, lbl=label_text, box=check_box: self.update_boolean_option(lbl, checked, box))

                option_label = QLabel(label_text)
                option_label.setFont(QFont("Arial", 14))
                option_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                option_label.setStyleSheet("color: black")

                layout.addWidget(check_box)
                layout.addWidget(option_label)
                layout.addStretch()
                container_widget = QWidget()
                container_widget.setLayout(layout)
                self.main_layout.addWidget(container_widget, row, col, 1, 3)
                self.boolean_options.append((option_label, check_box))

                # Update label initially based on preset value
                self.update_boolean_option(label_text, preset_value, check_box)

            def update_boolean_option(self, label_text, checked, box):
                for label, check_box in self.boolean_options:
                    if check_box == box:
                        if checked:
                            label.setText(f"{label_text} (True)")
                            label.setStyleSheet("color: green")
                        else:
                            label.setText(f"{label_text} (False)")
                            label.setStyleSheet("color: red")

            def add_numeric_option(self, option_name, label_text, row, col, min_val, max_val, step, preset_value):
                layout = QVBoxLayout()

                self.slider_layout = QHBoxLayout()
                self.label = QLabel(label_text)
                self.label.setFont(QFont("Arial", 14))
                self.label.setAlignment(Qt.AlignLeft)
                self.label.setStyleSheet("color: black")

                self.slider = QSlider(Qt.Horizontal)
                self.slider.setMinimum(int(min_val * 100))
                self.slider.setMaximum(int(max_val * 100))
                self.slider.setSingleStep(int(step * 100))
                self.slider.setValue(int(preset_value * 100))
                self.slider.valueChanged.connect(self.update_slider_label)

                self.slider_value_label = QLabel(f"{preset_value:.2f}")
                self.slider_value_label.setFont(QFont("Arial", 14))
                self.slider_value_label.setAlignment(Qt.AlignLeft)
                self.slider_value_label.setStyleSheet("color: black")

                self.plus_button = QPushButton("+")
                self.plus_button.setFixedSize(30, 30)
                self.plus_button.setStyleSheet("color: black;")
                self.plus_button.clicked.connect(lambda: self.adjust_slider_value(self.slider, step))

                self.minus_button = QPushButton("-")
                self.minus_button.setFixedSize(30, 30)
                self.minus_button.setStyleSheet("color: black;")
                self.minus_button.clicked.connect(lambda: self.adjust_slider_value(self.slider, -step))

                self.slider_layout.addWidget(self.minus_button)
                self.slider_layout.addWidget(self.slider)
                self.slider_layout.addWidget(self.plus_button)

                layout.addWidget(self.label)
                layout.addWidget(self.slider_value_label)
                layout.addLayout(self.slider_layout)
                container_widget = QWidget()
                container_widget.setLayout(layout)
                self.main_layout.addWidget(container_widget, row, col, 1, 3)

            def update_slider_label(self, value):
                self.slider_value_label.setText(f"{value / 100:.2f}")

            def adjust_slider_value(self, slider, step):
                current_value = slider.value()
                new_value = current_value + int(step * 100)
                slider.setValue(new_value)

            def add_choice_option(self, option_name, label_text, row, col, choices, preset_value):
                layout = QHBoxLayout()
                self.label = QLabel(label_text)
                self.label.setFont(QFont("Arial", 14))
                self.label.setAlignment(Qt.AlignLeft)
                self.label.setStyleSheet("color: black")

                self.choice_layout = QVBoxLayout()
                self.button_group = QButtonGroup()

                for choice in choices:
                    radio_button = QRadioButton(choice)
                    radio_button.setFont(QFont("Arial", 14))
                    radio_button.setStyleSheet("color: black")
                    if choice == preset_value:
                        radio_button.setChecked(True)
                    self.button_group.addButton(radio_button)
                    self.choice_layout.addWidget(radio_button)

                layout.addWidget(self.label)
                layout.addLayout(self.choice_layout)
                container_widget = QWidget()
                container_widget.setLayout(layout)
                self.main_layout.addWidget(container_widget, row, col, 1, 3)

            def save_options(self):
                options = {
                    'sat_threshold': self.slider.value() / 100,
                    'top_K_paths': 6,
                    'reranking': False,
                    'sat_type': 'count_occurrences',
                    'fitness_type': 'mean',
                    'cumulative_res': False,
                    'optimize_dt': self.boolean_options[0][1].isChecked(),
                    'print_dt': True,  # preset attivo di default
                    'compute_gain': False,
                    'smooth_factor': 1,
                    'num_classes': 2,
                    'train_prefix_log': self.boolean_options[1][1].isChecked(),
                    'one_hot_encoding': self.boolean_options[2][1].isChecked(),
                    'use_score': self.boolean_options[3][1].isChecked(),
                    'compute_baseline': False,
                    'Print_edit_distance': False,
                    'print_log': False,
                    'print_length': False,
                    'eval_stamp': False,
                    'recc_stamp': False,
                    'Allprint': False,
                    'weighted_prefix_generation': False,
                    'enable_log': False,
                    'Quick': False
                }

                with open("option.dat", "w") as f:
                    for key, value in options.items():
                        f.write(f"{key}={value}\n")

                with open("encoding.dat", "w") as f:
                    f.write("simple")

                # Passare alla finestra debug_window
                from debug_window import DebugWindow
                self.debug_window = DebugWindow("light")  # Usa "light" o "dark" a seconda del tema
                self.debug_window.show()
                self.close()

            def go_back(self):
                from encoding_window import EncodingWindow
                self.encoding_window = EncodingWindow()
                self.encoding_window.show()
                self.close()

        if __name__ == "__main__":
            app = QApplication(sys.argv)
            window = Option1Window()
            window.show()
            sys.exit(app.exec())

    def go_back(self):
        from encoding_window import EncodingWindow
        self.encoding_window = EncodingWindow()
        self.encoding_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Simpleencoding()
    window.show()
    sys.exit(app.exec())
