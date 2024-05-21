import sys
from PySide6.QtWidgets import *
from gui_main_window import MainWindow
from details_simple import DetailsSimpleWindow
from details_complex import DetailsComplexWindow
from details_declarative import DetailsDeclarativeWindow
from gui_dataset_window import DatasetWindow
from gui_terminal_window import TerminalWindow

class AppRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.current_title = "Main Window"

        # Initialize all window components
        self.main_window = MainWindow(self, self.switch_view_callback)
        self.details_simple_window = DetailsSimpleWindow(self.switch_view_callback)
        self.details_complex_window = DetailsComplexWindow(self.switch_view_callback)
        self.details_declarative_window = DetailsDeclarativeWindow(self.switch_view_callback)
        self.dataset_window = DatasetWindow(self.switch_view_callback)
        self.terminal_window = TerminalWindow(self.switch_view_callback)

        # Add all windows to the stack
        self.stack.addWidget(self.main_window)
        self.stack.addWidget(self.details_simple_window)
        self.stack.addWidget(self.details_complex_window)
        self.stack.addWidget(self.details_declarative_window)
        self.stack.addWidget(self.dataset_window)
        self.stack.addWidget(self.terminal_window)
        self.setCentralWidget(self.stack)

    def switch_view_callback(self, view_name):
        # A dictionary to map view names to methods
        view_methods = {
            'main': self.show_main_window,
            'simple': lambda: self.show_simple_details_window("Details - Simple"),
            'complex': lambda: self.show_complex_details_window("Details - Complex"),
            'declarative': lambda: self.show_declarative_details_window("Details - Declarative"),
            'dataset': lambda: self.show_dataset_window(self.current_title),
            'terminal': self.show_terminal_window
        }
        # Call the corresponding view method based on the input view name
        view_method = view_methods.get(view_name)
        if view_method:
            view_method()

    def show_main_window(self):
        self.stack.setCurrentWidget(self.main_window)

    def show_simple_details_window(self, title):
        self.current_title = title
        self.stack.setCurrentWidget(self.details_simple_window)

    def show_complex_details_window(self, title):
        self.current_title = title
        self.stack.setCurrentWidget(self.details_complex_window)

    def show_declarative_details_window(self, title):
        self.current_title = title
        self.stack.setCurrentWidget(self.details_declarative_window)

    def show_dataset_window(self, title):
        self.dataset_window.set_title(title)
        self.stack.setCurrentWidget(self.dataset_window)

    def show_terminal_window(self):
        self.stack.setCurrentWidget(self.terminal_window)

if __name__ == "__main__":
    app = QApplication([])
    runner = AppRunner()
    runner.show()
    app.exec()
