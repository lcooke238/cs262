import logging
import threading
import grpc
import chat_pb2
import chat_pb2_grpc
import sys
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import hashlib
from queue import Queue


LOG_PATH = "../logs/client_grpc.log"

# statuses
SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

# Setting a maximum allowed length for usernames and messages
MAX_USERNAME_LENGTH = 30
MAX_MESSAGE_LENGTH = 1000

# customize server address
HOST_IP = "localhost"
PORT = "50051"


class EventWatcher(FileSystemEventHandler):
    def __init__(self):
        self.old = 0
        self.delta = 0.1

    def hash_file(self, file):
        with open(file, 'rb', buffering=0) as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()

    def on_created(self, event):
        return super().on_created(event)

    def on_deleted(self, event):
        return super().on_deleted(event)
    
    def on_modified(self, event):
        statbuf = os.stat(event.src_path)
        new = statbuf.st_mtime
        if (new - self.old > self.delta):
            self.old = new
            print(event)
            print(self.hash_file(event.src_path))
            
        return super().on_modified(event)
    
    # Unusued methods for now

    # def on_any_event(self, event):
    #     return super().on_any_event(event) 

    # def on_closed(self, event):
    #     return super().on_closed(event)
    
    # def on_moved(self, event):
    #     return super().on_moved(event)

    # def on_opened(self, event):
    #     return super().on_opened(event)

class Client:

    def __init__(self, host=HOST_IP, port=PORT):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.user_token = ""
        self.server_online = False

    def __valid_username(self, user):
        return user and len(user) < MAX_USERNAME_LENGTH and user.isalnum()

    def attempt_login(self, condition):
        while True:
            user = input("Please enter a username: ")
            if self.__valid_username(user):
                break
            print(f"Invalid username - please provide an alphanumeric username of up to {MAX_USERNAME_LENGTH} characters.")

        # attempt login on server
        try:
            response = self.stub.Login(chat_pb2.LoginRequest(user=user))
        except:
            self.handle_server_shutdown()

        # if failure, print failure and return; they can attempt again
        if response.status == FAILURE:
            print(f"Login error: {response.errormessage}")
            return
        
        # if success, set user token and print success
        self.user_token = response.user
        print(f"Succesfully logged in as user: {self.user_token}. Unread messages:")

        # notify listener thread to start listening
        with condition:
            condition.notify_all()

    def attempt_logout(self):
        try:
            response = self.stub.Logout(chat_pb2.LogoutRequest(user=self.user_token))
        except:
            self.handle_server_shutdown()
        if response.status == FAILURE:
            print(f"Logout error: {response.errormessage}")
            return
        self.user_token = ""
        return

    def attempt_delete(self):
        try:
            self.stub.Delete(chat_pb2.DeleteRequest(user=self.user_token))
        except:
            self.handle_server_shutdown()
        self.user_token = ""
        return

    def handle_invalid_command(self, command):
        print(f"Invalid command: {command}, please try \\help for list of commands")

    def display_command_help(self):
        print(
        """
              -- Valid commands --
        \\help -> Gives this list of commands
        \\quit -> Exits the program
        \\logout -> logs out of your account
        \\delete -> deletes your account
        \\send message -> {target_user} -> sends message to target_user
        \\list {wildcard} -> lists all users that match the SQL wildcard provided, e.g. \\list % lists all users
        """
            )

    def process_command(self, command):
        if len(command) < 5:
            self.handle_invalid_command(command)
            return True
        if command[0:5] == "\\help":
            self.display_command_help()
            return True
        if command[0:5] == "\\quit":
            self.attempt_logout()
            return False
        if len(command) < 7:
            self.handle_invalid_command(command)
            return True
        if command[0:7] == "\\logout":
            self.attempt_logout()
            return True
        if command[0:7] == "\\delete":
            self.attempt_delete()
            return True
        self.handle_invalid_command(command)
        return True

    def ClientHandler(self, testing=False):
        self.stub = chat_pb2_grpc.ClientHandlerStub(self.channel)
        condition = threading.Condition()

        if testing:
            self.attempt_login(condition)
            return

        # start new Daemon thread listening for messages with condition variable
        # to sync with main thread to have blocking rather than polling
        thread = threading.Thread(target=self.listen, args=(condition,))
        thread.daemon = True
        thread.start()

        # We setup a thread to monitor file updates on the local machine
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        path = '.'
        event_handler = EventWatcher()
        # event_handler = LoggingEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()

        while True:
            if not self.server_online:
                self.handle_server_shutdown()
            try:
                if self.user_token:

                    command = input(f"{self.user_token} > ")
                    # if \quit is run, quit
                    if not self.process_command(command):
                        print("See you later!")
                        self.channel.close()
                        break
                else:
                    self.attempt_login(condition)
            except KeyboardInterrupt:  # for ctrl-c interrupt
                self.attempt_logout()
                self.channel.close()
                observer.stop()
                print("Logging you out!")
                break
        observer.join()

    def listen(self, condition):
        while True:
            if self.user_token:
                try:
                    response = self.stub.GetMessages(chat_pb2.GetRequest(user=self.user_token))
                except:
                    self.server_online = False
                    self.handle_server_shutdown()
                if response.status == SUCCESS_WITH_DATA:
                    print("")
                    for message in response.message:
                        print(f"\033[94m{message.sender} > \033[0m{message.message}")
                    print(f"{self.user_token} > ", end="")
            else:
                with condition:
                    condition.wait()

    def handle_server_shutdown(self):
        self.channel.close()
        os._exit(FAILURE)

    def run(self, testing=False):
        # initialize logs
        # logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.server_online = True
        self.ClientHandler(testing)


if __name__ == '__main__':
    client = Client()
    client.run()
