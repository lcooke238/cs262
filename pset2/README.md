# COMPSCI 262 PSET 2: Overall Notebook

## Introduction
This README gives a high level overview of the entire repository. This assignment is split into code and documentation sections. We have separate ```README.md``` files for specifics about each folder. Structure:
- code
    - ```machine.py```: code to run a single machine for the mock system.
- documentation
    - ```analysis.ipynb```: jupyter notebook to compute trends from experimental logs.
    - ```ledger.md```: notebook for design decisions.
    - ```lab_notebook.md```: notebook for analyzing experimental results.
    - ```graphs```: Stores the graphs for ```lab_notebook.md``` from the experiments.
- logs
    - ```experiment_1```: folder containing the logs from the first experiment.
        - ```log_0.txt```: text log for the machine with id 0.
        - ```log_1.txt```: text log for the machine with id 1.
        - ```log_2.txt```: text log for the machine with id 2.
    - ```experiment_2```: folder containing the logs from the second experiment.
        - ```log_0.txt```: text log for the machine with id 0.
        - ```log_1.txt```: text log for the machine with id 1.
        - ```log_2.txt```: text log for the machine with id 2.
    - ```experiment_3```: folder containing the logs from the third experiment.
        - ```log_0.txt```: text log for the machine with id 0.
        - ```log_1.txt```: text log for the machine with id 1.
        - ```log_2.txt```: text log for the machine with id 2.
    - ```experiment_4```: folder containing the logs from the fourth experiment.
        - ```log_0.txt```: text log for the machine with id 0.
        - ```log_1.txt```: text log for the machine with id 1.
        - ```log_2.txt```: text log for the machine with id 2.
    - ```experiment_5```: folder containing the logs from the fourth experiment.
        - ```log_0.txt```: text log for the machine with id 0.
        - ```log_1.txt```: text log for the machine with id 1.
        - ```log_2.txt```: text log for the machine with id 2.
- tests
    - ```test_unit.py```: unit test suite for one machine.
    - ```test_machine.py```: test suite for the interactions of three machines under fixed parameters.

## Installation requirements

1. Make sure that you have python 3.10 or later installed (to handle match statements).

2. To run the unit tests, you need to install pytest. You can do so using `pip install -U pytest`.

## To Run The System
1. Follow the installation requirements.

2. run the following lines in three separate terminals, and DO NOT press enter when prompted yet:
    - ```python3 machine.py 0```
    - ```python3 machine.py 1```
    - ```python3 machine.py 2```

3. You will see the following message displayed in each terminal:
    ```WELCOME TO THE MACHINE. WAIT FOR CONSENSUS, THEN CONFIRM YOUR MISSION.```
    When you see this displayed on every terminal, press ```ENTER``` in each terminal one at a time.

    Upon success, you should see the following message at the bottom of each window:
    ```"enter main loop, successful connections: 2```

4. Let all three machines run for as long as you would like the simulation to run, and quit the program once you are done. The results will be recorded in the log files within the ```logs``` folder.


## What the Logs Mean
Each ```log_[id].txt``` file, where ```[id]``` will be replaced with the machine id, will begin with the following line:

```LOG FOR MACHINE [id] WITH CLOCK SPEED [speed] ```

Here, ```[speed]``` represents the number of operations per minute the machine can execute.

From this point on, there are two possible types of logs you will see:
1. ```[logical clock time] - [system time]: [operation].```
2. ```[logical clock time] - [system time]: Received message: [logical clock time of reciept]. Queue length: [current queue length].```
All of the text in brackets represents the actual parameter explained within that text. 

## Running the tests

1. We have two tests files, `test_unit.py` which has a number of basic unit tests, and `test_machine.py` which is more of an integration test, actually running three machines and checking they interact as we would expect.

2. `test_unit.py` can just be run using `pytest` when within the tests folder, since it just tests each unit/method of the Machine class. `test_machine.py` requires you to set three machines running and setting the flags in `machine.py` to testing settings so that we have deterministic behavior to be able to log as we would expect. You need to have all machines running for at least 15 seconds for these tests to work (since it checks the behavior for each over the first 15 seconds that they were running).

## Experiment Analysis

The analysis for our experiments is within the `documentation` folder, with the code in `analysis.ipynb` but the actual written analysis (with the graphs and the highlights of the data) in `lab_notebook.md`.