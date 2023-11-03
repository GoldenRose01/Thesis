# Outcome-Oriented Prescriptive Process Monitoring: Generazione di Raccomandazioni con Simple Index Encoding
This repository contains the source code of a prescriptive process monitoring system that provides recommendations for achieving a positive outcome of an ongoing process using the simple index encoding. The recommendations specify which activities to perform and when to execute them. The work is based on  the system available at this [link](https://github.com/ivanDonadello/temporal-prescriptive-process-monitoring_old.git), which establishes temporal relationships among the activities executed within the process to provide recommendations.

## Requirements
The following python package are required:
- python tested with version 3.11.5
- pandas tested with version 2.0.2
- numpy tested with version 1.25.0
- PM4PY tested with version 2.7.4
- sklearn tested with version 1.2.2

## How to run
First of all, clone this repo. Then add the input logs in the folder <code>media/input</code>. The logs used in this experiments are available [here](https://drive.google.com/file/d/1DDP7OKQhD8cno2tbSpLlIPZ-Mh5y-XUC/view). The <code>settings.py</code> file contains the configuration parameters for the experiments.
To run the experiment type:
```
$ python run_experiments.py
```
The result are available in the folder <code>media/output</code>.


