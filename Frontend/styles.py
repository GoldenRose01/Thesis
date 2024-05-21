# Mappa dei colori
color_map = {
    "default": "#f0f0f0",
    "simple": "#add8e6",
    "complex": "#ffb6c1",
    "declarative": "#90ee90",
    "selected": "#ffd700",
    'button': '#0078d7',
    'button_hover': '#005a9e',
    'button_pressed': '#003776',
    'dataset_button': '#00aaff',
    'dataset_button_hover': '#0077cc',
    'dataset_button_pressed': '#004499',
    'title_selected': '#00ff00',  # Verde per i titoli selezionati
    'title_unselected': '#808080',  # Grigio più scuro per i titoli non selezionati
}

# Stile per i pulsanti
button_style = """
QPushButton {
    background-color: %s;
    color: white;
    border-radius: 5px;
    padding: 10px;
    font-size: 14px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: %s;
}
QPushButton:pressed {
    background-color: %s;
}
""" % (color_map['button'], color_map['button_hover'], color_map['button_pressed'])

dataset_button_style = """
QPushButton {
    background-color: %s;
    color: white;
    border-radius: 5px;
    padding: 5px;  
    font-size: 12px;
}
QPushButton:hover {
    background-color: %s;
}
QPushButton:pressed {
    background-color: %s;
}
""" % (color_map['dataset_button'], color_map['dataset_button_hover'], color_map['dataset_button_pressed'])

# Stile per la finestra principale
main_window_style = """
QWidget {
    background-color: %s;
}
""" % color_map['default']

# Stile per la finestra dei dettagli
selected_color_map = {
    "simple": "#40E0D0",  # Turchese
    "complex": "#FFA500",  # Arancione
    "declarative": "#98FF98"  # Verde menta
}

# Stile per il QLabel del titolo
title_label_style = """
QLabel {
    font-size: 18px;
    color: #333;
    padding: 10px 0;
    background-color: inherit;  # Inherit the background color from the parent
}
"""

# Stile per il QLabel della descrizione
description_label_style = """
QLabel {
    font-size: 14px;
    color: #333;
    padding: 5px 0;
    background-color: inherit;  # Inherit the background color from the parent
}
"""

# Stile per i titoli con checkbox
title_checkbox_style = """
QCheckBox {
    font-size: 14px;
    padding: 5px;
    spacing: 10px;
    background-color: inherit;  # Inherit the background color from the parent
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
"""
