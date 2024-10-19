import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtSvgWidgets import QSvgWidget

class LoadingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setGeometry(100, 100, 1440, 720)

        self.svg_widget = QSvgWidget("Frontend/svg/Sigillo_Università_di_Trento.svg")
        self.setCentralWidget(self.svg_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_main_window)
        self.timer.start(2500)  # 2,5 secondi di caricamento

    def show_main_window(self):
        self.timer.stop()
        from encoding_window import EncodingWindow
        self.main_window = EncodingWindow()
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loading_window = LoadingWindow()
    loading_window.show()
    sys.exit(app.exec())
