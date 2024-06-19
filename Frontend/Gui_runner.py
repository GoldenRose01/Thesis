import sys
import traceback
from PyQt6.QtCore import *
from PyQt6.QtSvgWidgets import *
from PyQt6.QtWidgets import *

from details_complex import DetailsComplexWindow
from details_declarative import DetailsDeclarativeWindow
from details_simple import DetailsSimpleWindow
from gui_dataset_window import DatasetWindow
from gui_main_window import MainWindow
from gui_terminal_window import TerminalWindow
from theme_selection_widget import ThemeSelectionWidget
from loading_window import LoadingWindow

from styles import *


class AppRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.current_title = "Main Window"
        self.color_map = color_map_light  # Default theme

        # Initialize all window components
        try:
            self.main_window = MainWindow(self.switch_view_callback, self.color_map)
            self.details_simple_window = DetailsSimpleWindow(self.switch_view_callback, self.color_map)
            self.details_complex_window = DetailsComplexWindow(self.switch_view_callback, self.color_map)
            self.details_declarative_window = DetailsDeclarativeWindow(self.switch_view_callback, self.color_map)
            self.dataset_window = DatasetWindow(self.switch_view_callback, self.color_map)
            self.terminal_window = TerminalWindow(self.switch_view_callback, self.color_map)
        except Exception as e:
            print(f"An error occurred during window initialization: {e}")
            traceback.print_exc()

        # Add all windows to the stack
        self.stack.addWidget(self.main_window)
        self.stack.addWidget(self.details_simple_window)
        self.stack.addWidget(self.details_complex_window)
        self.stack.addWidget(self.details_declarative_window)
        self.stack.addWidget(self.dataset_window)
        self.stack.addWidget(self.terminal_window)
        self.setCentralWidget(self.stack)

    def set_theme(self, theme):
        if theme == "light":
            self.color_map = color_map_light
        else:
            self.color_map = color_map_dark

        # Update all windows with the new theme
        self.update_theme_for_all_windows()

    def switch_view_callback(self, view_name):
        try:
            view_methods = {
                'main': self.show_main_window,
                'simple': lambda: self.show_simple_details_window("Details - Simple"),
                'complex': lambda: self.show_complex_details_window("Details - Complex"),
                'declarative': lambda: self.show_declarative_details_window("Details - Declarative"),
                'dataset': lambda: self.show_dataset_window(self.current_title),
                'terminal': self.show_terminal_window,
                'update_theme': self.update_theme_for_all_windows
            }
            view_method = view_methods.get(view_name)
            if view_method:
                view_method()
            else:
                raise ValueError(f"Unknown view name: {view_name}")
        except Exception as e:
            print(f"An error occurred while switching view: {e}")
            traceback.print_exc()

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

    def update_theme_for_all_windows(self):
        self.main_window.update_color_map(self.color_map)
        self.details_simple_window.update_color_map(self.color_map)
        self.details_complex_window.update_color_map(self.color_map)
        self.details_declarative_window.update_color_map(self.color_map)
        self.dataset_window.update_color_map(self.color_map)
        self.terminal_window.update_color_map(self.color_map)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        """
        # Create and display the loading window
        loading_window = LoadingWindow()
        loading_window.show()
        """
        # Create and display the main application window after the loading window is closed
        def show_main_app():
            runner = AppRunner()
            runner.show()

        QTimer.singleShot(5000, show_main_app)  # Show the main application window after 5 seconds
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
