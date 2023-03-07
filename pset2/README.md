# COMPSCI 262 PSET 2: Overall Notebook

## Introduction
This readme gives a high level overview of the entire repository. This assignment is split into code and documentation sections. We have separate ```README.md``` files for specifics about each folder. Structure:
- code
    - ```machine.py```: code to run a single machine for the mock system.
- documentation
    - ```ledger.md```: notebook for design decisions
    - ```lab_notebook.md```: notebook for analyzing experimental results
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
- tests
    - ```test_machine.py```: test suite for the implementation of a single machine

## To Run The Experiment
1. Make sure that you have python 3.10 or later installed.

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