## Installation Instructions
To run the custom wire version of our chat application, you will need to have python version 3.10 or higher installed to support the match statements used. The installation link can be found here: https://www.python.org/downloads/release/python-3100/

You will then need to install the following packages:

- socket
- select
- pandas
- warnings

you can install each module by running the following lines:
-> run ```python3 -m pip install socket```
-> run ```python3 -m pip install select```
-> run ```python3 -m pip install pandas```
-> run ```python3 -m pip install warnings```

## Running Instructions
To run the custom wire version of our chat application, you must do the following:

1. connect all laptops to the same wifi network.
2. Find the IP address of the laptop you wish to be the server.
3. Per client machine, set ```server_host``` to be the IP address of the server laptop in ```client_custom.py```
4. For the server machine, set ```server_host``` to be the IP address of the server laptop in ```server_custom.py```
5. Run ```server_custom.py``` on the laptop for the server
6. Run ```client_custom.py``` on each client machine. 
