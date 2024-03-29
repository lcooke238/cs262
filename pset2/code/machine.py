# imports
import random
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

# experimental constants; adjust for testing's sake
MAX_RANDOM_STATE = 10
USE_MANUAL_CLOCK_RATES = False
manual_clock_rates = {
            0: 1,
            1: 2,
            2: 6,
        }
USE_MANUAL_STATES = False
manual_states = {
            0: [4] * 14 + [1] + [4] * 10000,
            1: [4] * 14 + [2] + [4] * 10000,
            2: [4] * 19 + [3] + [4] * 10000,
        }

# folder for logs; either should be "" or end in /
LOG_FOLDER = ""

# MessageType class: limits message types to RECIEVED, SENT_ONE, SENT_TWO, and INTERNAL
class MessageType(Enum):
    RECEIVED = 0
    SENT_ONE = 1
    SENT_TWO = 2
    INTERNAL = 3

class Machine():
    def __init__(self, id):
        self.id = id
        self.clock = 0
        self.freq = random.randint(1, 6)
        if USE_MANUAL_CLOCK_RATES:
            self.freq = manual_clock_rates[self.id]
        self.queue = queue.Queue()
        log_name = "../logs/" + LOG_FOLDER + "log_" + str(id) + ".txt"
        self.log_file = open(log_name, "w")
        self.log_file.write(f"LOG FOR MACHINE {self.id} WITH CLOCK SPEED {self.freq}\n")
        self.log_file.flush()
        self.listen_socket = None
        self.write_sockets = {}
        self.cv = threading.Condition()
        self.successful_connections = 0
        print(f"Machine with id {self.id} successfully initialized with clock speed {self.freq}")

    def send(self, machine_id_list):
        for id in machine_id_list:
            # get socket and attempt to convert message to send
            sock = self.write_sockets[id]
            try:
                wire = int.to_bytes(self.clock, MESSAGE_SIZE)
            except OverflowError:
                print("Overflow error.")
                sys.exit(1)

            # send over socket
            sock.sendall(wire)

        # log appropriately
        if len(machine_id_list) == 1:
            self.log(MessageType.SENT_ONE, data=machine_id_list[0])
        else:
            self.log(MessageType.SENT_TWO)

    def log(self, message_type, data=None):
        # depending on message type, log a standard log message to the log file for this machine
        match message_type:
            case MessageType.RECEIVED if data != None:
                self.log_file.write(f"{self.clock} - {time.time()}: Received message: {data}. Queue length: {self.queue.qsize()}.\n")
            case MessageType.SENT_ONE if data != None:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent one message to machine {data}.\n")
            case MessageType.SENT_TWO:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent two messages.\n")
            case MessageType.INTERNAL:
                self.log_file.write(f"{self.clock} - {time.time()}: Internal event.\n")
            case _:
                self.log_file.write(f"{self.clock} - {time.time()}: ERROR, Invalid message type.\n")
        self.log_file.flush()

    def make_action(self, testing_value = None):
        # if the queue is not empty, use that
        if not self.queue.empty():
            clock = int.from_bytes(self.queue.get())
            self.clock = max(self.clock, clock) + 1
            self.log(MessageType.RECEIVED, data=clock)

        # if the queue is empty, randomize between sending or internal event
        else:
            self.clock += 1
            random_action = random.randint(1, MAX_RANDOM_STATE) if not(testing_value) else testing_value
            if USE_MANUAL_STATES and manual_states[self.id]:
                random_action = manual_states[self.id].pop(0)
            match random_action:
                case 1:
                    self.send([(self.id + 1) % 3])
                case 2:
                    self.send([(self.id + 2) % 3])
                case 3:
                    self.send([(self.id + 1) % 3, (self.id + 2) % 3])
                case _:
                    self.log(MessageType.INTERNAL)

    # handles a single connection, run by a single thread
    def receive_messages(self, con):
        # polls for messages
        while True:
            try:
                message = con.recv(MESSAGE_SIZE)
                if not message:
                    self.shutdown()
                self.queue.put(message)
            except:
                self.shutdown()

    def listen(self):
        with self.cv:
            print("Listen socket started listening")
            self.listen_socket.listen()

            # accept 2 connections
            for i in range(2):
                con, addr = self.listen_socket.accept() 
                print(f"successffully accepted connection {i + 1}")
                self.successful_connections += 1
                # Setup a thread to receive messages on that connection
                thread = threading.Thread(target=self.receive_messages, args=(con, ))
                thread.daemon = True
                thread.start()

            print("Listen socket accepted connections with both other machines")

            # all listen connections established; notify main thread that
            # if it has completed all of its write connections, it is good to go.
            self.cv.notify_all()

    def init_sockets(self):
        # setup our listener socket to listen
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((SOCKET_IP, SOCKET_PORT_BASE + self.id))
        self.listen_socket = listen_socket

        # create sockets that we will use to write to the two other machines
        for id in [elt for elt in [0, 1, 2] if elt != self.id]:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.write_sockets[id] = new_socket

    def connect_write_sockets(self):
        # for each socket we want to connect to
        for id, sock in self.write_sockets.items():
            # simply poll, attempt to connect. if fail, try again. 
            while True:
                try:
                    sock.connect((SOCKET_IP, SOCKET_PORT_BASE + id))
                    print(f"Successfully connected to machine {id} via write socket")
                    break
                except:
                    continue
        print("All write sockets connected")
        return

    def run(self):
        # initialize sockets
        self.init_sockets()
        print("Sockets initialized")
        input("WELCOME TO THE MACHINE. INITIALIZE ALL PARTICIPANTS, THEN HIT ENTER.")

        # setup the listening system. this will then create its own children threads for each connection
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()

        # in the main thread, attempt to connect to the two write sockets
        self.connect_write_sockets()

        # If we reach here, we have connected to the two write sockets.
        # It might be the listener thread hasn't started (seems unlikely) in which case main thread
        # will acquire this cv first. But then it will fail the self.successfull_connections check, and let the listener thread go.
        # In what seems more likely, the listener is already going. Either it has completed, in which case we can acquire this cv
        # and run the main logic, or it hasn't, and we block here until those are set, when we will get notified and run.
        with self.cv:
            print(f"enter main loop, successful connections: {self.successful_connections}")
            interval = 1 / self.freq
            while not self.successful_connections == 2:
                self.cv.wait()

            # Both listen and write sockets are setup, so we loop forever, making actions as our clock speed allows
            while True:
                try:
                    start_time = time.time()
                    self.make_action()
                    # Sleeping appropriately to keep clock frequency
                    time.sleep(interval - (time.time() - start_time))
                except:
                    self.shutdown()

    def shutdown(self, testing = False):
        # Cleanup our sockets and our log files
        self.listen_socket.close()
        for _, sock in self.write_sockets.items():
            sock.close()
        self.log_file.close()
        if not testing:
            sys.exit(0)

def main():
    # verify user input
    if len(sys.argv) != 2:
        print("Usage: py machine.py {MACHINE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)
    try:
        id = int(sys.argv[1])
    except:
        print("Usage: py machine.py {MACHINE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)
    if not id in [0, 1, 2]:
        print("Usage: py machine.py {MACHINE_ID}. id should be one of 0, 1, 2 and unique.")
        sys.exit(1)

    # run
    machine = Machine(id)
    machine.run()

if __name__ == "__main__":
    main()
