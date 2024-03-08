import sys
from PySide6.QtWidgets import *
from gui_main_window import MainWindow
from gui_details_window import DetailsWindow
from gui_run_window import RunWindow

class AppRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()

        self.main_window = MainWindow(self)
        self.details_window = DetailsWindow(self.switch_view_callback,)
        self.run_window = RunWindow(self)

        self.stack.addWidget(self.main_window)
        self.stack.addWidget(self.details_window)
        self.stack.addWidget(self.run_window)

        self.setCentralWidget(self.stack)

    def switch_view_callback(self, view_name):
        # Logic to switch between different views based on view_name
        if view_name == 'main':
            self.main_window.show()
            self.details_window.hide()
            # Handle other views accordingly
        elif view_name == 'details':
            self.details_window.show()
            self.main_window.hide()

    def show_main_window(self):
        self.stack.setCurrentWidget(self.main_window)

    def show_details_window(self, encoding):
        self.details_window.update_for_encoding(encoding)
        self.stack.setCurrentWidget(self.details_window)

    def show_run_window(self):
        self.stack.setCurrentWidget(self.run_window)

if __name__ == "__main__":
    app = QApplication([])
    runner = AppRunner()
    runner.show()
    app.exec()