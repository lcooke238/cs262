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
        - try running again w a smaller variation in clock cycles and a smaller probability of the event being internal. What differences do those variations make? Try to find something interesting.
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

To communicate these messages between clients over the wire, we would need to either setup a custom wire protocol for this assignment or use gRPC to define an encoding. Both will be simpler than the last assignment, as we only have a single type of message to deal with and a single type of input message to handle. 

Ultimately, we chose to use direct socketing and a custom wire protocol. This was the pseudocode for our plan:
```
# initialization function:
    # set clock tick rate bw 1 and 6 randomly
    # connect to other machines in system
    # open a log file
    # create unconstrained network queue to hold incoming messages
    # listen to all sockets for messages

# run a clock cycle function:
    # until logical clock steps run out:
        # if there is a message in the queue for the machine (do some select work here):
            # take message off queue
            # update logical clock
            # log message reciept, global system time, length of network queue, logical clock time
        # if there is no message in queue:
            # generate random number between 1 and 10 inclusive:
                # if 1:
                    # send a message to one of the existing machines that contains the local logical clock time
                    # update its own logical clock
                    # log the send, system time, and logical clock time
                # if 2:
                    # send to other machine message that is the local logical clock time
                    # update its own logical clock
                    # log the send, system time, and the logical clock time
                # if 3: 
                    # send to both other machines message that is the local logical clock time
                    # update its own logical clock
                    # log the send, system time, and logical clock time
                # else:
                    # update local logical clock
                    # log internal event, system time, and logical clock time

# maintain queue function (probably should run before each clock cycle, unrestricted power): 
    # find sockets with information on them (messages for reciept)
    # per message on socket:
        # recieve it according to wp spec
        # add it in proper format to network queue

# log function
    # given message to log and filename, write message to new line of the file
```

## Errors

1. Socket closure - if one of the machines shuts down, we can no longer send messages to them from the other machines, nor receive messages. This will mess with all of our results, so this will be treated as a catastrophic failure where every machine shuts down.

2. Operating System Differences - on Windows and Linux, when we run our code it works perfectly, however on MacOS the code can only connect to sockets that were created before the thread was created, despite polling working correctly. To fix this, we added a pause in our code using an input statement that allows the user to wait for all three machines to be created and have their sockets created before threading begins on any machine.

## Day-by-day

### Wednesday 1st March

Today I set up the framework for all the machine logic except the actual socket communication. I created a Machine class, which upon initialization picks a random frequency between 1-6 to run at. You initialize the machines with an id - we will use 0, 1, 2 as the ids for the machines.

We decided to attempt direct communication to try something new. Our idea is:

* Each machine listens on the same IP (running on the same laptop, callback address) but with a different port (some set BASE_PORT + the id of the machine, so that each machine has a unique port to make life easier). Each machine attempts to connect to the other two possible ports.

* This will be tricky without probably a few layers of multi-threading. When a machine runs, we want it to:

    * Setup a port to listen on and wait until it accepts 2 connections

    * Attempt to connect to each of the other 2 machines

* We can't do simply do this in a single-threaded system. If we had every machine listen for connections, and then attempt to connect to the other machines, they would all get stuck listening for each other while none of them would ever actually attempt a connection.

* As such, we created a listen method for the machine which will run in its own thread. However, we still need to do some more thinking about how to get this to work nicely - it seems like condition variables will be useful to communicate between the threads that the listener thread has accepted all the connections and the main thread has succesfully connected to the other two sockets.

While we figure those issues out, we tried to layout the bulk of the other code (i.e all the stuff that doesn't involve the socket communication, which isn't that much honestly). Each machine has a queue (we could just use the socket, but it felt cleanest to have an explicit queue).

We have a log function that writes to a log file (also initialized based upon the machine id) and a make_action function that picks the random number between 1-10 and takes the relevant action (although currently without actually sending anything, because the socket stuff isn't setup).

### Thursday 2nd March

Now we're cooking. Here's how my socket communication works:

* In the run method of the machine, we do the following:

    * Initialize the sockets using `init_sockets`. This simply creates the socket objects for the socket we will listen on, and the two sockets we will use to send messages to the other two machines.

    * We setup a thread that runs the `listen` method.

        * This thread acquires the condition variable and starts listening with our listener socket. It accepts two connections.

            * For each connection it accepts, we start a new thread that receives messages from that connection.
        
        * Once it has done its job and started those other two threads, this thread uses `notify_all` to notify the main thread that it is about to release the condition variable, and then exits.
    
    * In the main thread, we poll to try to connect to the other two sockets we are expecting to be opened by the other machines.

    * If we get past that in the main thread, we have established a write connection to the other two. We attempt to gain the condition variable: this ensures that we wait for the listener thread to have accepted the two listen connections too.

    * We then loop forever, making an action as our clock frequency permits. We sleep the relevant amount of time after each action to ensure that we do at most `self.freq` actions per second.

This all seems to work and behave reasonably nicely. The main things that clearly need to be worked on are whether I can do this without the condition variable (it certaintly seems like the else condition is unnecessary), there is a redundant lock that I'm about to remove, and reformatting the times more nicely. I'm also interested if we can use the library mentioned on Ed to avoid having to do the three terminal setup.

Then for the experiments, it seems like it could be tricky to shut the machines down after 60s to collect data.


## Monday 6th March: Experiments
Today, we developed some experiments to run using our machines to discuss the size of jumps in the vals for the logical clocks, the drift in the values of the local logical clocks in the different machines (compared to system time), and the impact different timings on such things as gaps in the logical clock vals and length of the message queue. To do this, we designed five separate experiments:
1. *Default*: Clock randomization was in the default 1-6 range and our machine action randomization was also in the default 1-10 range.
2. *Identical speeds*: Our machine randomization remained the same (between 1 and 10), however our clock randomization ceased to be random, and all machines ran with the same speed of 2.
3. *No Internal Events*: Our clock randomization was the default 1-6 range, however, we removed the possibility of an internal event occuring by keeping the machine randomization between 1 and 3.
4. *Fast machines, more internal events*: We manually set the clock rates of the three machines to 4, 5, and 6, while greatly biasing the machine randomization in favor of internal events by having the random number generated uniformly between 1 and 250.
5. *Slow machines, only internal events*: only internal events ever happen, with clock rates 1, 2, and 3.

We also designed an ```analysis.ipynb``` notebook to do some general analysis of our logs and produce visualizations for the relationships between our logical clocks.

Overall, we found that the logical clock model has been a useful tool for tracking the order of events in a distributed system, allowing us to order events properly without knowing the exact time that they occured on the system. We saw that the size of jumps in the logical clock values can vary depending on the frequency and timing of events, and that the length of the message queue can also vary depending on the frequency and timing of events. We also thought a bit about the limitations of this simulation in understanding network behavior, ignoring things like network latency, message loss, and machine failures that could all impact the ordering of events.

## Tuesday 7th March: Tests

Unit tests were largely finalized around this date. Our approach to unit testing was two-pronged; the first prong deals more with ensuring that every function works by itself in a vacuum (this is likely what's usually meant by the term unit testing), while the second deals with testing the holistic functionality of the entire machine in a specific test case. The first batch of tests can be found in tests/test_unit.py, and ensure basic functions like `Machine.init()`, `Machine.log()`, and `Machine.make_action()` work as intended. The second batch can be found in tests/test_machine.py, where one can also find an extensive discussion of the example that the machine's output is being tested against.

The large example tested against in test_machine.py only works due to the consistency of logical clock rules; using those rules, we can determine exactly what the outputted logs of each of the machines should look like in a very specific case. To ensure this case happens when we run machine.py, we added MANUAL_STATES, which can be configured to feed each of the machines a very specific sequence of internal events and send events. This way, we remove all random number generation from the process, and thus guarantee a trio of logs we can test for exact values.