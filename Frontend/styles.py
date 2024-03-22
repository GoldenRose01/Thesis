# Mappa dei colori
color_map = {
    "default": "#f0f0f0",
    "simple": "#add8e6",
    "complex": "#ffb6c1",
    "declarative": "#90ee90",
    "selected": "#ffd700",
}

# Stile per i pulsanti
button_style = """
QPushButton {
    background-color: #007bff;
    color: white;
    border-radius: 4px;
    padding: 6px;
    font-size: 14px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #0056b3;
}
QPushButton:pressed {
    background-color: #003885;
}
"""

# Stile per la finestra principale
main_window_style = """
QWidget {
    background-color: #f0f0f0;
}
"""

# Stile per la finestra dei dettagli
selected_color_map = {
    "simple": "#40E0D0",  # Turchese
    "complex": "#FFA500",  # Arancione
    "declarative": "#98FF98"  # Verde menta
}
title_label_style = """
QLabel {
    font-size: 18px;
    color: #333;
    padding: 10px 0;
}
"""