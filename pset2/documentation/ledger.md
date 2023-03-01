# Assignment 2: Asynchronous Distributed System Model

## Assignment Spec (Synthesis)
Building a model of a small, asynchronous distributed system. Runs on a single machine, modelling multiple machines running at different speeds. Pieces of the system:
1. Machine initialization
    - each virtual machine will do the following:
        - have a logical clock, running at clock rate determined at initialization as follows:
            - pick random number 1 thru 6 representing number of clock ticks per real world second for that machine (represents number of instructions that can be run at that time)
            - update logical clock according to rules for logical clocks
        - should connect to each of the other virtual machines s.t. messages can be passed bw them (part of initialization, unconstrained by clocks)
        - open a file as a log
        - have a network queue (unconstrained by above number of ops per second) to hold incoming messages
        - should listen to 1+ sockets for messages
2. Spec for operations post-initialization
    - per clock cycle:
        - if there is a message in the message queue for the machine:
            - the machine should take one message off of the queue
            - update logical clock
            - write in log that it recieved a message, the global time from system, length of message queue, and logical clock time
        - if there is no message in the queue:
            - machine generates random number between 1 and 10 inclusive:
                - if 1: 
                    - send a message to one of the machines that contains the local logical clock time
                    - update its own logical clock
                    - update the log with the send, system time, and logical clock time
                - if 2:
                    - send to other machine message that is the local logical clock time
                    - update its own logical clock
                    - update log with the send, system time, and the logical clock time
                - if 3: 
                    - send to both other machines message that is the local logical clock time
                    - update its own logical clock
                    - update the log with the send, system time, and logical clock time
                - if 4-10:
                    - update local logical clock
                    - log internal event, system time, and logical clock time
3. documentation requirements
    - keep notebook for design decisions
    - run scale model at least 5 times for at least one minute each time and record the following in notebook:
        - examine logs and discuss the size of jumps in the vals for the logical clocks, drift in the vals of the local logical clocks in the different machines (compared to system time), and the impact different timings on such things as gaps in the logical clock vals and length of the msg queue
            - include observations and reflections abt the model and the results of running the model
        - try running again w a smaller variation in clock cucles and a smaller probability of the event being internal. What differences do those variations make? Try to find something interesting.
4. Other notes
    - can use whatever packages or support code for the construction of the model machines and for the communication between the processes
    - will turn in both the code and the lab notebook.
    - will demo this, presenting code and choices, on Mar 8 (demo day 2)
    - 3 machines minimum/required --> can all be run on a single machine
    - sockets give you an automatic queue?


## Design
In writing out the design for a single machine in this mock distributed system, I ran into some initial trouble with how to initially connect all of the different machines. Here are some options I am considering:
    1. create communications server: initialize a server to handle all message sending between clients. On startup in experimental pipeline, have the machines connect to a set server as clients.
    2. direct socketing: have each client function as a server and a client. Here, machine initialization would require each machine to setup its own server. Then, after initialization, we would have to connect to all servers and each server would only handle messages for its respective machine.
Simply based on my familiarity with the first option from the first assignment, I am leaning more towards option 1.

To communicate these messages between clients over the wire, we would need to either setup a custom wire protocol for this assignment or use gRPC to define an encoding. Both will be simpler than the last assignment, as we only have a single type of message to deal with and a single type of input message to handle. 



## Errors
