def save_type_encoding(encoding_type):
    with open('../Encoding.dat','w') as file:
        file.write(encoding_type)

def select_datasets(selected_datasets):
    # Sovrascrive il file datasets_names.dat con i nuovi datasets selezionati
    with open('../Datasets_names.dat', 'w') as file:
        for dataset in selected_datasets:
            file.write(f'{dataset}\n')

def update_option(option_key, option_value):
    # Leggi il contenuto esistente
    updated_lines = []
    option_found = False
    with open('../Option.dat', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith(option_key + ' ='):
                updated_lines.append(f'{option_key} = {option_value}\n')
                option_found = True
            else:
                updated_lines.append(line)

    # Aggiorna il file solo se l'opzione è stata trovata e modificata
    if option_found:
        with open('../Option.dat', 'w') as file:
            file.writelines(updated_lines)
