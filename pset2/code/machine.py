# imports
import random
import logging
import queue
import socket
import threading
import time
import numpy as np
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
        log_name = "../logs/log_" + str(id) + ".txt"
        self.log_file = open(log_name, "w")
        self.listen_socket = None
        self.write_sockets = {}
        self.cv = threading.Condition()
        self.lock = threading.Lock()
        self.succesful_connections = 0
        print(f"Machine with id {self.id} succesfully initialized with clock speed {self.freq}")


    def send(self, machine_id_list):
        for id in machine_id_list:
            # Send over socket
            sock = self.write_sockets[id]
            try:
                wire = int.to_bytes(self.clock, 8)
            except OverflowError:
                print("Overflow error.")
                sys.exit(1)
            sock.sendall(wire)
        if len(machine_id_list) == 1:
            self.log(MessageType.SENT_ONE)
        else:
            self.log(MessageType.SENT_TWO)
        return
    
    def log(self, message_type):
        match message_type:
            case MessageType.RECEIVED:
                self.log_file.write(f"{self.clock} - {time.time()}: Received message. Queue length: {self.queue.qsize}.\n")
            case MessageType.SENT_ONE:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent one message.\n")
            case MessageType.SENT_TWO:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent two messages.\n")
            case MessageType.INTERNAL:
                self.log_file.write(f"{self.clock} - {time.time()}: Internal event.\n")
        self.log_file.flush()
        return

    def make_action(self):
        if not self.queue.empty:
            _ = self.queue.get()
            self.log(MessageType.RECEIVED)
        else:
            random_action = random.randint(1, 10)
            match (random_action):
                case 1:
                    self.send([(self.id + 1) % 3])
                case 2:
                    self.send([(self.id + 2) % 3])
                case 3:
                    self.send([(self.id + 1) % 3, (self.id + 2) % 3])
                case _:
                    self.log(MessageType.INTERNAL)
        # We think log before clock increase, but unclear in spec. Could also go above if/else for opposite effect
        self.clock += 1

    def receive_messages(self, con):
        while True:
            try:
                message = con.recv(MESSAGE_SIZE)
                self.queue.put(message)
            except:
                self.shutdown()

    def listen(self):
        # TODO: Handle CTRL+C shutdown etc
        with self.cv:
            print("Listen socket started listening")
            self.listen_socket.listen()
            # Accept 2 connections
            for i in range(2):
                con, addr = self.listen_socket.accept() 
                print(f"succesfully accepted connection {i + 1}")
                self.succesful_connections += 1
                thread = threading.Thread(target=self.receive_messages, args=(con, ))
                thread.daemon = True
                thread.start()
            print("Listen socket accepted connections with bother other machines")
            self.cv.notify_all()

        

    def init_sockets(self):
        # Setup our listener socket to listen
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((SOCKET_IP, SOCKET_PORT_BASE + self.id))
        self.listen_socket = listen_socket

        # Wait until we can connect to the other sockets we would like to be able to write to.
        for id in [elt for elt in [0, 1, 2] if elt != self.id]:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.write_sockets[id] = new_socket

    def connect_write_sockets(self):
        for id, sock in self.write_sockets.items():
            while True:
                try:
                    sock.connect((SOCKET_IP, SOCKET_PORT_BASE + id))
                    print(f"Succesfully connected to machine {id} via write socket")
                    break
                except:
                    continue
        print("All write sockets connected")
        return

    def run(self):
        self.init_sockets()
        print("Sockets initialized")
        # Pretty sure we need three threads, 2 listener threads.
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()
        # If we get past this, we can write to the other two sockets
        self.connect_write_sockets()
        with self.cv:
            print(f"enter main loop, succesful connections: {self.succesful_connections}")
            interval = 1 / (self.freq)
            if self.succesful_connections == 2:
                while True:
                    start_time = time.time()
                    self.make_action()
                    # Sleeping appropriately to keep clock frequency
                    time.sleep(interval - (time.time() - start_time))
            else:
                self.cv.wait()

    def shutdown(self):
        self.listen_socket.close()
        self.log_file.close()

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