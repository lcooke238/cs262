# imports
import random
import logging
import queue
import time
# constants


# initialization function:
    # set clock tick rate bw 1 and 6 randomly
    # connect to other machines in system
    # open a log file
    # create unconstrained network queue to hold incoming messages
    # listen to all sockets for messages


class Machine():
    def __init__(self, id):
        self.id = id
        self.clock = 0
        self.freq = random.randint(1, 6)
        self.queue = queue.Queue()
        log_name = "log_" + id + ".txt"
        self.log = open(log_name, "w")
    
    def init_sockets(self):
        pass

    def send(self, machine_id_list, info):
        # log within the send
        pass
    
    def log(self):
        pass

    def make_action(self):
        if self.queue:
            pass
        else:
            random_action = random.randint(1, 10)
            match (random_action):
                case 1:
                    self.send([(self.id + 1) % 3], self.clock)
                case 2:
                    self.send([(self.id + 2) % 3], self.clock)
                case 3:
                    self.send([(self.id + 1) % 3, (self.id + 2) % 3], self.clock)
                case _:
                    self.log(INTERNAL_EVENT)
            self.clock += 1
                    
                    

    def run(self):
        interval = 1 / (self.freq)
        while True:
            start_time = time.time()
            self.make_action()
            time.sleep(interval - (time.time() - start_time))

    def shutdown(self):
        self.log.close()

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
