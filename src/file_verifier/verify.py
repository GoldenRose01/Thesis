import subprocess
import os
# ___Verifica se i file Resource_att.txt e Trace_att.txt esistono nella cartella desiderata___#
def attributes_verifier(directory):
    resource_filename = "Resource_att.txt"
    trace_filename = "Trace_att.txt"
    resource_att_path = directory + "/" + resource_filename
    trace_att_path = directory + "/" + trace_filename
    if not os.path.exists(resource_att_path) or not os.path.exists(trace_att_path):
        print("File non trovati. Esecuzione dello script script csvreader.")
        subprocess.run(["python", "Mediamanager/csvreader.py"])
    else:
        print("File trovati,inizio esperimento")

def remove_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            os.remove(os.path.join(directory, filename))
    print("File eliminati")