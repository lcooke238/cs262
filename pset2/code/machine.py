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
        self.queue = queue.Queue()
        log_name = "../logs/log_" + str(id) + ".txt"
        self.log_file = open(log_name, "w")
        self.listen_socket = None
        self.write_sockets = {}
        self.cv = threading.Condition()
        self.succesful_connections = 0
        print(f"Machine with id {self.id} succesfully initialized with clock speed {self.freq}")


    def send(self, machine_id_list):
        for id in machine_id_list:
            # Get socket and attempt to convert message to send
            sock = self.write_sockets[id]
            try:
                wire = int.to_bytes(self.clock, 8)
            except OverflowError:
                print("Overflow error.")
                sys.exit(1)
            # Send over socket
            sock.sendall(wire)
        # Log appropriately
        if len(machine_id_list) == 1:
            self.log(MessageType.SENT_ONE, data=machine_id_list[0])
        else:
            self.log(MessageType.SENT_TWO)
    
    def log(self, message_type, data=None):
        # Depending on message type, log a standard log message to the log file for this machine
        match message_type:
            case MessageType.RECEIVED if data:
                self.log_file.write(f"{self.clock} - {time.time()}: Received message: {data}. Queue length: {self.queue.qsize()}.\n")
            case MessageType.SENT_ONE if data:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent one message to machine {data}.\n")
            case MessageType.SENT_TWO:
                self.log_file.write(f"{self.clock} - {time.time()}: Sent two messages.\n")
            case MessageType.INTERNAL:
                self.log_file.write(f"{self.clock} - {time.time()}: Internal event.\n")
            case _:
                self.log_file.write(f"{self.clock} - {time.time()}: ERROR, Invalid message type.\n")
        self.log_file.flush()

    def make_action(self):
        # If the queue is not empty, use that
        if not self.queue.empty():
            clock = int.from_bytes(self.queue.get())
            self.clock = max(self.clock, clock) + 1
            self.log(MessageType.RECEIVED, data=clock)
        # If the queue is empty, randomize between sending or internal event
        else:
            self.clock += 1
            random_action = random.randint(1, 10)
            match random_action:
                case 1:
                    self.send([(self.id + 1) % 3])
                case 2:
                    self.send([(self.id + 2) % 3])
                case 3:
                    self.send([(self.id + 1) % 3, (self.id + 2) % 3])
                case _:
                    self.log(MessageType.INTERNAL)

    def receive_messages(self, con):
        # Handles a single connection run by a single thread
        # Polls for messages
        while True:
            try:
                message = con.recv(MESSAGE_SIZE)
                # TODO: Should check for empty message here to shutdown, can't remember syntax,
                # can I literally check if not message?
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
                # Setup a thread to receive messages on that connection
                thread = threading.Thread(target=self.receive_messages, args=(con, ))
                thread.daemon = True
                thread.start()
            print("Listen socket accepted connections with both other machines")
            # All listen connections established, notify main thread that, if it has completed all of its write connections
            # it is good to go.
            self.cv.notify_all()

    def init_sockets(self):
        # Setup our listener socket to listen
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((SOCKET_IP, SOCKET_PORT_BASE + self.id))
        self.listen_socket = listen_socket

        # Create sockets that we will use to write to the two other machines
        for id in [elt for elt in [0, 1, 2] if elt != self.id]:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.write_sockets[id] = new_socket

    def connect_write_sockets(self):
        # For each socket we want to connect to
        for id, sock in self.write_sockets.items():
            # Simply poll, attempt to connect. If fail, try again. 
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
        # Initialize sockets
        self.init_sockets()
        print("Sockets initialized")
        input("WELCOME TO THE MACHINE. WAIT FOR CONSENSUS, THEN CONFIRM YOUR MISSION. HELL TO THE YEAH BROTHERS N SISTERS.")
        # Setup the listening system. This will then create its own children threads for each connection
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()
        # In the main thread, attempt to connect to the two write sockets
        self.connect_write_sockets()
        # If we reach here, we have connected to the two write sockets.
        # It might be the listener thread hasn't started (seems unlikely) in which case main thread
        # will acquire this cv first. But then it will fail the self.successfull_connections check, and let the listener thread go.
        # In what seems more likely, the listener is already going. Either it has completed, in which case we can acquire this cv
        # and run the main logic, or it hasn't, and we block here until those are set, when we will get notified and run.
        with self.cv:
            print(f"enter main loop, succesful connections: {self.succesful_connections}")
            interval = 1 / self.freq
            while not self.succesful_connections == 2:
                self.cv.wait()
            # Both listen and write sockets are setup, so we loop forever, making actions as our clock speed allows
            while True:
                start_time = time.time()
                self.make_action()
                # Sleeping appropriately to keep clock frequency
                time.sleep(interval - (time.time() - start_time))

    def shutdown(self):
        # Cleanup our sockets and our log files
        self.listen_socket.close()
        self.log_file.close()

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