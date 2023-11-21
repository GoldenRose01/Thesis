import tkinter as tk
from tkinter import ttk

def run_settings():
    print("Settings Run")
    # Here you can add the code to handle the settings

# Create the main window
root = tk.Tk()
root.title("Settings")
root.configure(bg='black')

# Define settings
settings = {
    'reranking': False,
    'sat_type': 'count_occurrences',
    'fitness_type': 'mean',
    'cumulative_res': False,
    # Add other settings here...
}

# Function to update a boolean setting
def update_bool_setting(setting):
    settings[setting] = not settings[setting]
    update_buttons()

# Function to update the GUI elements
def update_buttons():
    for setting, button in toggle_buttons.items():
        button.config(bg='green' if settings[setting] else 'red')

# Create toggle buttons for boolean settings
toggle_buttons = {}
for idx, setting in enumerate(['reranking', 'cumulative_res', 'optmize_dt', 'print_dt', 'compute_gain', 'train_prefix_log', 'one_hot_encoding', 'use_score', 'compute_baseline']):
    button = tk.Button(root, text=setting, bg='red', command=lambda s=setting: update_bool_setting(s))
    button.grid(row=idx, column=0, pady=2, padx=5)
    toggle_buttons[setting] = button

# Dropdown for sat_type
sat_type_var = tk.StringVar(value=settings['sat_type'])
sat_type_dropdown = ttk.Combobox(root, textvariable=sat_type_var, values=['count_occurrences', 'count_activations', 'strong'])
sat_type_dropdown.grid(row=1, column=1, pady=2, padx=5)

# Slider for smooth_factor
smooth_factor_var = tk.DoubleVar(value=settings.get('smooth_factor', 1))
smooth_factor_slider = tk.Scale(root, from_=0, to=5, resolution=0.25, orient='horizontal', variable=smooth_factor_var)
smooth_factor_slider.grid(row=2, column=1, pady=2, padx=5)

# Update the button states initially
update_buttons()

# Run Button
run_button = tk.Button(root, text="RUN", command=run_settings)
run_button.grid(row=10, column=0, columnspan=2, pady=5, padx=5)

root.mainloop()
