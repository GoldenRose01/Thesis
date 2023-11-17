# Outcome-Oriented Prescriptive Process Monitoring: Generazione di Raccomandazioni con  Index Encoding
This repository contains the source code of a prescriptive process monitoring system that provides recommendations for achieving a positive outcome of an ongoing process using a simple or complex index encoding. The recommendations specify which activities to perform and when to execute them. The work is based on  the system available at this [link](https://github.com/ivanDonadello/temporal-prescriptive-process-monitoring_old.git), which establishes temporal relationships among the activities executed within the process to provide recommendations.

# Instruction for running the experiments
Clone this repo,then follow the instructions below.
## Requirements
Run req.bat to install all the libraries needed for the project.
Secondly add the input logs in the folder <code>media/input</code>. The logs used in this experiments are available [here](https://drive.google.com/file/d/1DDP7OKQhD8cno2tbSpLlIPZ-Mh5y-XUC/view). The <code>settings.py</code> file contains the configuration parameters for the experiments.
To run the experiment type:
```
$ python run_experiments.py
```
The result are available in the folder <code>media/output</code>.

# Project based on work of Luca Boschiero
The repository of his work can be found there [here](https://github.com/lucaboschiero/tesi)