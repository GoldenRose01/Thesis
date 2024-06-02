# styles.py

# Mappa dei colori
color_map_light = {
    "default": "#ffffff",
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
    'title_selected': '#00ff00',
    'title_unselected': '#808080',
}

color_map_dark = {
    "default": "#333333",
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
    'title_selected': '#00ff00',
    'title_unselected': '#808080',
}

def get_contrasting_text_color(background_color):
    # Convert hex to RGB
    background_color = background_color.lstrip('#')
    bg_r = int(background_color[0:2], 16)
    bg_g = int(background_color[2:4], 16)
    bg_b = int(background_color[4:6], 16)

    # Calculate brightness (YIQ)
    brightness = (bg_r * 299 + bg_g * 587 + bg_b * 114) / 1000
    return '#000000' if brightness > 128 else '#ffffff'

# Stile per i pulsanti trasparenti
button_style = """
QPushButton {
    background-color: transparent;
    color: %s;
    border: 2px solid %s;
    border-radius: 5px;
    padding: 10px;
    font-size: 14px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.2);
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.3);
}
"""

dataset_button_style = """
QPushButton {
    background-color: transparent;
    color: %s;
    border: 2px solid %s;
    border-radius: 5px;
    padding: 5px;  
    font-size: 12px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.2);
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.3);
}
"""

# Stile per la finestra principale
main_window_style = """
QWidget {
    background-color: %s;
}
"""

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
    color: %s;
    padding: 10px 0;
    background-color: inherit;
}
"""

# Stile per il QLabel della descrizione
description_label_style = """
QLabel {
    font-size: 14px;
    color: %s;
    padding: 5px 0;
    background-color: inherit;
}
"""

# Stile per i titoli con checkbox
title_checkbox_style = """
QCheckBox {
    font-size: 14px;
    padding: 5px;
    spacing: 10px;
    color: %s;
    background-color: inherit;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
"""
