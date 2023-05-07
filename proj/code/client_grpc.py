import logging
import threading
import grpc
import file_pb2
import file_pb2_grpc
from time import sleep
import sys
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import hashlib
import uuid
from queue import Queue, SimpleQueue
from ast import literal_eval

LOG_PATH = "../logs/client_grpc.log"

# statuses
SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

# Database constants
OWNER = 10
EDITOR = 11

# File path
FILE_PATH = os.path.abspath("../files/")

# Setting a maximum allowed length for usernames and messages
MAX_USERNAME_LENGTH = 30
MAX_MESSAGE_LENGTH = 1000

# Size of chunks to stream
CHUNK_SIZE = 1024 * 10

# Rate at which to poll server for updates in seconds
SYNC_RATE = 4

# customize server address
HOST_IP = "localhost"
PORT = "50051"

def hash_file(file):
    with open(file, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').digest()

class EventWatcher(FileSystemEventHandler):
    def __init__(self, stub, user_token):
        self.old = 0
        self.delta = 0.1
        self.stub = stub
        self.user_token = user_token
        self.client_clock = 0

    def on_created(self, event):
        return super().on_created(event)

    def on_deleted(self, event):
        return super().on_deleted(event)

    def __push(self, path):
        print(f"\nLocal modification detected at {path}.")
        logging.info(f"Local modification detected at {path}.")

        # We hash the file
        hash = hash_file(path)
        # Get MAC address
        MAC_addr = literal_eval(hex(uuid.getnode()))
        # Process the event source path
        filepath, filename = os.path.split(path)
        safe_filepath = filepath.replace("\\", "/")

        # We check the file to see if it is the same as on the server (no action needed)
        request = file_pb2.CheckRequest(user=self.user_token, hash=hash, clock=self.client_clock)
        try:
            response = self.stub.Check(request)
        except Exception as e:
            logging.error(e)
            print(e)
            print("hi")
            self.shutdown(FAILURE)

        # If the response tells use we need to send an update, we send
        if response.sendupdate:
            # Add metadata
            send_queue = Queue()
            send_queue.put(file_pb2.UploadRequest(meta=
                            file_pb2.Metadata(clock=0,
                                             user=self.user_token,
                                             hash=hash,
                                             MAC=MAC_addr,
                                             filename=filename,
                                             filepath=safe_filepath)
                            )
                        )

            # Add 10KB chunks
            with open(path) as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    block = bytes(data, "utf-8")
                    send_queue.put(file_pb2.UploadRequest(file=block))

            # Add sentinel to mark stream termination
            send_queue.put(None)

            # Send grpc request
            try:
                response = self.stub.Upload(iter(send_queue.get, None))
            except Exception as e:
                logging.error(e)
                print(e)
                print("hi here")
                self.shutdown(FAILURE)

            if response.status == SUCCESS:
                print(f"Local modification at {path} uploaded to server successfully.")
                logging.info(f"Push to server for {path} complete.")
        return

    def on_modified(self, event):
        # Dodging double detection issue
        statbuf = os.stat(event.src_path)
        new = statbuf.st_mtime

        # Need to avoid getting this on directories
        if event.is_directory:
            return

        # By checking if the two events were separated by a small delta time, if not, return
        if (new - self.old < self.delta):
            return

        # Otherwise, update last update time
        self.old = new

        # Push modification to server
        self.__push(event.src_path)
        return

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
        self.backups = []

    def attempt_backup_connect(self):
        if not self.backups:
            return False
        backup = self.backups.pop()
        # Set host and port to new settings
        self.host = backup.host
        self.port = backup.port
        # Update the channel, closing the previous
        self.channel.close()
        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.stub = file_pb2_grpc.ClientHandlerStub(self.channel)
        return True

    def attempt_setup_backups(self):
        response = self.stub.GetBackups(file_pb2.BackupRequest())
        try:
            for backup in response.serverinfo:
                self.backups.append(backup)
        except:
            while self.attempt_backup_connect():
                if self.attempt_setup_backups():
                    return True
            return False
        return True

    def __valid_username(self, user):
        return user and len(user) < MAX_USERNAME_LENGTH and user.isalnum()

    def attempt_login(self, condition):
        while True:
            user = input("Please enter a username: ")
            if self.__valid_username(user):
                break
            print(f"Invalid username - please provide an alphanumeric username of up to {MAX_USERNAME_LENGTH} characters.")

        # attempt login on server
        response = self.stub.Login(file_pb2.LoginRequest(user=user))

        # if failure, print failure and return; they can attempt again
        if response.status == FAILURE:
            print(f"Login error: {response.errormessage}")
            return

        # if success, set user token and print success
        self.user_token = response.user
        print(f"Successfully logged in as user: {self.user_token}.")

        # notify listener thread to start listening
        with condition:
            condition.notify_all()

    def attempt_logout(self):
        self.user_token = ""
        return

    def attempt_list(self):
        response = self.stub.List(file_pb2.ListRequest(user=self.user_token))

        # if failed, print failure and return
        if response.status == FAILURE:
            print(f"List users error: {response.errormessage}")
            return

        # if success, print users that match the wildcard provided
        if response.files:
            print(f"Files available to you:")
            for file in response.files:
                print(file)
        else:
            print("You have no files available.")
        return

    def attempt_delete(self):
        response = self.stub.Delete(file_pb2.DeleteRequest(user=self.user_token))
        self.user_token = ""
        return

    def handle_invalid_command(self, command):
        print(f"Invalid command: {command}, please try \\help for list of commands")

    def display_command_help(self):
        print(
        """
              -- Valid commands --
        \\help -> provides the text you're seeing now
        \\list -> lists files you have access to
        \\logout -> logs you out of your account
        \\delete -> deletes all of your files from server, logs you out
        \\quit -> exits the program
        """
            )

    def process_command(self, command):
        if (len(command) < 5):
            self.handle_invalid_command(command)
            return True
        if command[0:5] == "\\help":
            self.display_command_help()
            return True
        if command[0:5] == "\\list":
            self.attempt_list()
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
        self.stub = file_pb2_grpc.ClientHandlerStub(self.channel)
        condition = threading.Condition()

        # try to setup backups
        self.attempt_setup_backups()

        if testing:
            logging.info("Testing!")
            self.attempt_login(condition)
            return

        # start new Daemon thread listening for messages with condition variable
        # to sync with main thread to have blocking rather than polling
        thread = threading.Thread(target=self.listen, args=(condition,))
        thread.daemon = True
        thread.start()
        logging.info("Listener thread up.")

        # We setup a thread to monitor file updates on the local machine
        path = FILE_PATH

        while True:
            if not self.server_online:
                observer.stop()
                logging.error("Server not online.")
                self.shutdown(FAILURE)
            try:
                if self.user_token:
                    command = input(f"{self.user_token} > ")
                    # if \quit is run, quit
                    if not self.process_command(command):
                        logging.warning("Quitting...")
                        self.shutdown(SUCCESS)
                else:
                    self.attempt_login(condition)
                    logging.info(f"Logged in as {self.user_token}.")

                    # after logging in, begin observer thread
                    event_handler = EventWatcher(self.stub, self.user_token)
                    observer = Observer()
                    observer.schedule(event_handler, path, recursive=True)
                    observer.start()
                    logging.info("Observer thread up.")
            except KeyboardInterrupt:  # for ctrl-c interrupt
                observer.stop()
                logging.warning("Keyboard interrupt.")
                self.attempt_logout()
                self.shutdown(SUCCESS)
            except Exception as e:
                safe = False
                while self.attempt_backup_connect():
                    try:
                        if self.user_token:
                            self.process_command(command)
                        else:
                            self.attempt_login(condition)
                        safe = True
                        break
                    except:
                        continue
                if not safe:
                    logging.error(e)
                    self.shutdown(FAILURE)
        observer.join()

    def __pull(self):
        # First building metadata of local files
        local_files = [os.path.join(dirpath,f).replace("\\", "/") for (dirpath, dirnames, filenames) in os.walk(FILE_PATH) for f in filenames]
        request = file_pb2.SyncRequest(user=self.user_token)
        MAC_addr = literal_eval(hex(uuid.getnode()))
        for file in local_files:
            filepath, filename = os.path.split(file)
            request.metadata.append(file_pb2.Metadata(clock=0,
                                                        user=self.user_token,
                                                        hash=hash_file(file),
                                                        MAC=MAC_addr,
                                                        filename=filename,
                                                        filepath=filepath))

        try:
            responses = self.stub.Sync(request)
        except Exception as e:
            logging.error(e)
            print(e)
            self.shutdown(FAILURE)


        data = bytearray()
        file_received = False
        filename = None
        filepath = None
        for r in responses:
            if r.HasField("will_receive"):
                break
            else:
                try:
                    if r.HasField("meta"):
                        if file_received:
                            print()
                            path = os.path.abspath(filepath)
                            os.makedirs(path, exist_ok=True)
                            with open(os.path.join(filepath, filename), "wb") as f:
                                f.write(data)
                                data = bytearray()

                        filename = r.meta.filename
                        filepath = r.meta.filepath
                        file_received = True
                        print(f"Successful sync at {r.meta.filepath}/{r.meta.filename}.")
                    else:
                        data.extend(r.file)
                except Exception as e:
                    print(e)

        # Catch last file
        try:
            if data != b"":
                path = os.path.abspath(filepath)
                os.makedirs(path, exist_ok=True)
                with open(os.path.join(filepath, filename), "wb") as f:
                    f.write(data)
                    data = bytearray()
            print(f"Successful sync at {r.meta.filepath}/{r.meta.filename}.")
        except Exception as e:
            print("Problem here")
            print(e)

    def listen(self, condition):
        while True:
            if self.user_token:
                try:
                    self.__pull()
                except Exception as e:
                    safe = False
                    while self.attempt_backup_connect():
                        try:
                            if (self.user_token):
                                self.__pull()
                            else:
                                self.attempt_login(condition)
                            safe = True
                            break
                        except:
                            continue
                    if not safe:
                        logging.error(e)
                        self.shutdown(FAILURE)
                sleep(SYNC_RATE)
            else:
                with condition:
                    condition.wait()

    def shutdown(self, status):
        self.channel.close()
        print("Goodbye!")
        logging.warning("Shutting down.")
        os._exit(status)

    def run(self, testing=False):
        # initialize logs
        logging.basicConfig(filename=LOG_PATH,
                            filemode='w',
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)
        logging.info("Starting client...")

        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.server_online = True
        self.ClientHandler(testing)


if __name__ == '__main__':
    client = Client()
    client.run()
