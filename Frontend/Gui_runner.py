import sys
from PySide6.QtWidgets      import *
from gui_main_window        import MainWindow
from gui_details_window     import DetailsWindow
from gui_run_window         import RunWindow
from gui_terminal_window    import TerminalWindow

class AppRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()

        self.encoding = "default"

        self.main_window = MainWindow(self,self.switch_view_callback)
        self.details_window = DetailsWindow(self.switch_view_callback)
        self.run_window = RunWindow(self.switch_view_callback)
        self.terminal_window = TerminalWindow(self.switch_view_callback)

        self.stack.addWidget(self.main_window)
        self.stack.addWidget(self.details_window)
        self.stack.addWidget(self.run_window)
        self.stack.addWidget(self.terminal_window)

        self.setCentralWidget(self.stack)

    def switch_view_callback(self, view_name):
        # Logic to switch between different views based on view_name
        if view_name == 'main':
            self.main_window.show()
            self.details_window.hide()
            self.run_window.hide()
            # Add other windows to hide if necessary
        #elif view_name in ["simple", "complex", "declarative"]:
        #    self.show_details_window(view_name)
        #    self.main_window.hide()
        #    self.run_window.hide()
        elif view_name == 'run':
            self.main_window.hide()
            self.details_window.hide()
            self.run_window.show()
        elif view_name == 'terminal':
            self.main_window.hide()
            self.details_window.hide()
            self.run_window.hide()
            self.terminal_window.show()

    def show_main_window(self):
        self.stack.setCurrentWidget(self.main_window)

    def show_details_window(self, encoding):
        self.details_window.set_encoding(encoding)
        self.stack.setCurrentWidget(self.details_window)

    def show_run_window(self):
        self.stack.setCurrentWidget(self.run_window)

if __name__ == "__main__":
    app = QApplication([])
    runner = AppRunner()
    runner.show()
    app.exec()