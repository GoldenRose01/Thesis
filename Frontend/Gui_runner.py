import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette
from loading_window import LoadingWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Imposta lo stile Fusion per un aspetto uniforme

    # Applicare il tema scuro iniziale
    dark_theme = True  # Impostare a True per iniziare con il tema scuro

    palette = app.palette()
    if dark_theme:
        palette.setColor(QPalette.ColorRole.Window, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
    else:
        palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
    app.setPalette(palette)

    loading_window = LoadingWindow()
    loading_window.show()
    sys.exit(app.exec())
