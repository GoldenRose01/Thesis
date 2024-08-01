# Outcome-Oriented Prescriptive Process Monitoring: Generazione di Raccomandazioni con  Index Encoding
This repository contains the source code of a prescriptive process monitoring system that provides recommendations for achieving a positive outcome of an ongoing process using a simple or complex index encoding. The recommendations specify which activities to perform and when to execute them. The work is based on  the system available at this [link](https://github.com/ivanDonadello/temporal-prescriptive-process-monitoring_old.git), which establishes temporal relationships among the activities executed within the process to provide recommendations.

# Instruction for running the experiments
Clone this repo,then follow the instructions below.

## Requirements
Verify if the .venv is present if not the libraries needed will be displayed in <code>requirements.txt</code>
Create a .env file in the root folder and add the <code>C:</code> path to <code>Graphviz\bin</code> 

Secondly add the input logs in the folder <code>media/input</code>. The logs used in this experiments are available [here](https://drive.google.com/file/d/1DDP7OKQhD8cno2tbSpLlIPZ-Mh5y-XUC/view). The <code>option.dat</code> file contains the configuration parameters for the experiments and the <code>Encoding.dat</code> let you choose the encoding type.
To run the experiment type:
```
$ python main.py
```
The result will be available in the folder <code>media/output</code>.

## Frontend Block
The frontend block is available in the folder <code>frontend</code>.It let you have a more User-friendly interface for running the experiment. Please note that not all the option of the frontend are 100% functioning(Declarative button and setting of it are present but not implemented).
```
$ cd Fontend
$ python Gui_runner.py 
```
## Postprocessing Block
If needed a more organzied structure, after the run of the main part, you can use the <code>src/file_verifier/reorganizer.py</code> and then the <code>src/file_verifier/processinginpost.py</code> to move the result folder in subgroups and then scan all the files to ave in the <code>media/postprocessing</code> folder the summary of all the data.

# Project based on work of Luca Boschiero
The repository of his work can be found there [here](https://github.com/lucaboschiero/tesi)