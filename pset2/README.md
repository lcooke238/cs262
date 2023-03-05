# COMPSCI 262 PSET 2: Overall Notebook

## Introduction
This readme gives a high level overview of the entire repository. This assignment is split into code and documentation sections. We have separate ```README.md``` files for specifics about each folder. Structure:
- code
    - ```machine.py```: code to run a single machine for the mock system, need to run three instances to run the experiment.
- documentation
    - ```ledger.md```: notebook for design decisions
    - ```lab_notebook.md```: notebook for analyzing experimental results
- logs
    - ```log_0.txt```: text log for the machine with id 0.
    - ```log_1.txt```: text log for the machine with id 1.
    - ```log_2.txt```: text log for the machine with id 2.
- tests
    - ```test_machine.py```: test suite for the implementation of a single machine

## To Run The Experiment
1. Make sure that you have python 3.10 or later installed.

2. run the following lines in three separate terminals:
    ```python3 machine.py 0```
    ```python3 machine.py 1```
    ```python3 machine.py 2```