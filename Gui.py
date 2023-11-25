import tkinter as tk
from tkinter import ttk

def open_settings(encoding_type):
    settings_window = tk.Toplevel(root)
    settings_window.title(f"{encoding_type} Settings")
    settings_window.configure(bg='black')
    # Add the settings widgets to 'settings_window' instead of 'root'
    # ... Rest of your settings window code ...

def create_main_window():
    main_window = tk.Tk()
    main_window.title("Encoding Selection")
    main_window.geometry('300x200')

    simplex_button = tk.Button(main_window, text="Simplex Encoding", command=lambda: open_settings("Simplex"))
    simplex_button.pack(pady=10)

    complex_button = tk.Button(main_window, text="Complex Encoding", command=lambda: open_settings("Complex"))
    complex_button.pack(pady=10)

    main_window.mainloop()

# Call the function to create and show the main window
create_main_window()

def run_settings():
    print("Settings Run")
    # Add code to handle the settings here

def create_rounded_button(parent, width, height, text, command):
    frame = tk.Frame(parent, bg='black')
    canvas = tk.Canvas(frame, width=width, height=height, bg='black', highlightthickness=0)
    canvas.pack(side='left')

    # Create rounded corners
    rad = 10  # Radius of the corners
    canvas.create_arc((2, 2, 2*rad, 2*rad), start=90, extent=90, fill='black')
    canvas.create_arc((width-2*rad, 2, width-2, 2*rad), start=0, extent=90, fill='black')
    canvas.create_arc((width-2*rad, height-2*rad, width-2, height-2), start=270, extent=90, fill='black')
    canvas.create_arc((2, height-2*rad, 2*rad, height-2), start=180, extent=90, fill='black')
    canvas.create_rectangle(rad, 2, width-rad, height-2, fill='black', outline='black')
    canvas.create_rectangle(2, rad, width-2, height-rad, fill='black', outline='black')

    # Label as the button
    label = tk.Label(frame, text=text, fg='white', bg='black')
    label.pack(fill='both', expand=True)
    label.bind('<Button-1>', lambda e: command())

    return frame

def update_bool_setting(setting):
    settings[setting] = not settings[setting]
    update_buttons()

def update_buttons():
    for setting, frame in toggle_buttons.items():
        label = frame.winfo_children()[1]  # Label is the second child
        label.config(bg='green' if settings[setting] else 'red')

def arrange_widgets():
    column_count = 2  # Set the number of columns
    row, col = 0, 0
    for widget in all_widgets:
        widget.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
        col += 1
        if col >= column_count:
            col = 0
            row += 1
    # Place the RUN button
    run_button.grid(row=row, column=0, columnspan=column_count, padx=10, pady=10, sticky='ew')

# Create the main window
root = tk.Tk()
root.title("Settings")
root.configure(bg='black')
root.geometry('500x600')  # Initial window size

# Define settings
settings = {
    'reranking': False,
    'cumulative_res': False,  # Ensure this key is included
    'optimize_dt': True,
    'print_dt': True,
    'compute_gain': False,
    'smooth_factor': 1,
    'train_prefix_log': False,
    'one_hot_encoding': False,
    'use_score': True,
    'compute_baseline': False,
    'sat_type': 'count_occurrences',  # Include this if used in the GUI
    'fitness_type': 'mean',  # Include this if used in the GUI
    # Add any other settings that are used in the GUI
}

# Create toggle buttons and other widgets
toggle_buttons = {}
all_widgets = []
for setting in ['reranking', 'cumulative_res', 'optimize_dt', 'print_dt', 'compute_gain', 'train_prefix_log', 'one_hot_encoding', 'use_score', 'compute_baseline']:
    button_frame = create_rounded_button(root, 100, 30, setting, lambda s=setting: update_bool_setting(s))
    toggle_buttons[setting] = button_frame
    all_widgets.append(button_frame)

sat_type_var = tk.StringVar(value=settings['sat_type'])
sat_type_dropdown = ttk.Combobox(root, textvariable=sat_type_var, values=['count_occurrences', 'count_activations', 'strong'])
all_widgets.append(sat_type_dropdown)

smooth_factor_var = tk.DoubleVar(value=settings.get('smooth_factor', 1))
smooth_factor_slider = tk.Scale(root, from_=0, to=5, resolution=0.25, orient='horizontal', variable=smooth_factor_var)
all_widgets.append(smooth_factor_slider)

# Run Button
run_button = tk.Button(root, text="RUN", command=run_settings)
all_widgets.append(run_button)

# Arrange widgets and update button states
arrange_widgets()
update_buttons()

root.mainloop()
