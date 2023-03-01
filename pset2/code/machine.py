# imports
import random
import logging
import queue
import socket
import threading
import time
from enum import Enum
import sys
# constants

MESSAGE_SIZE = 8

SOCKET_IP = "127.0.0.1"
SOCKET_PORT_BASE = 8000

class MessageType(Enum):
    RECEIVED = 0
    SENT_ONE = 1
    SENT_TWO = 2
    INTERNAL = 3



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
        self.log_file = open(log_name, "w")
        self.listen_socket = None
        self.write_sockets = []

    def send(self, machine_id_list, info):
        # log within the send
        for id in machine_id_list:
            # Send over socket
            pass
        if len(machine_id_list) == 1:
            self.log(MessageType.SENT_ONE)
        else:
            self.log(MessageType.SENT_TWO)
            
        pass
    
    def log(self, message_type):
        match message_type:
            case MessageType.RECEIVED:
                self.log_file.write(f"{self.clock} - {time.time()}: Received message. Queue length: {self.queue.qsize}.")
            case MessageType.SENT_ONE:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent one message.")
            case MessageType.SENT_TWO:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent two messages.")
            case MessageType.INTERNAL:
                self.log_file.write(f"{self.clock} - {time.time()}: Internal event.")
        return

    def make_action(self):
        if self.queue:
            front = self.queue.get()

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
                    self.log(MessageType.INTERNAL)
        # We think log before clock increase, but unclear in spec. Could also go above if/else for opposite effect
        self.clock += 1
                    
    def listen(self):
        # Handle CTRL+C shutdown etc
        while True:
            message = self.listen_socket.recv(MESSAGE_SIZE)
            self.queue.put(message)

    def init_sockets(self):
        # Setup our listener socket to listen
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((SOCKET_IP, str(SOCKET_PORT_BASE + self.id)))

        # Wait until we can connect to the other sockets we would like to be able to write to.
        

    def run(self):
        self.init_sockets()
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()
        interval = 1 / (self.freq)
        while True:
            start_time = time.time()
            self.make_action()
            # Sleeping appropriately to keep clock frequency
            time.sleep(interval - (time.time() - start_time))

    def shutdown(self):
        self.listen_socket.close()
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

def main():
    if len(sys.argv) != 2:
        print("Usage: py machine.py {MACIHNE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)
    try:
        id = int(sys.argv[1])
    except:
        print("Usage: py machine.py {MACIHNE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)
    if not id in [0, 1, 2]:
        print("Usage: py machine.py {MACIHNE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)
    machine = Machine(id)
    machine.run()

if __name__ == "__main__":
    main()