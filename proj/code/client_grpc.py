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
import time

LOG_PATH = "../logs/client_grpc.log"

# DEMO code to manually alter MAC for demonstration purposes
MAC_DEMO = 0

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

# Function to hash file to binary
def hash_file(file):
    with open(file, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').digest()

class EventWatcher(FileSystemEventHandler):
    def __init__(self, stub, user_token, host, port, channel, backups):

        # Used for filtering out double modification detections (watchdog bug)
        self.old = 0
        self.delta = 0.1

        # Server info
        self.host = host
        self.port = port
        self.channel = channel
        self.stub = stub
        self.backups = backups

        # User info
        self.user_token = user_token
        self.client_clock = 0

        # Used for checking for MOVEs rather than creations
        self.move_queue = Queue()
        
    # Shutdown connection for observer thread
    def shutdown(self):
        try:
            self.channel.close()
        except:
            pass


    
    def attempt_backup_connect(self):
        # If out of backups, fail
        if not self.backups:
            return False
        
        # Pull next backup
        backup = self.backups.pop()

        # Set host and port to new settings
        self.host = backup.host
        self.port = backup.port

        # Update the channel, closing the previous
        self.channel.close()
        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.stub = file_pb2_grpc.ClientHandlerStub(self.channel)

        print(f"New connection on: {self.host}: {self.port}")
        return True

    # Safe move function with backup functionality
    def safe_move(self, old_src, dest_src, dest_filepath, dest_filename):
        try:
            self.stub.Move(file_pb2.MoveRequest(
                                                    old_src=old_src, 
                                                    dest_src=dest_src,
                                                    dest_filepath=dest_filepath,
                                                    dest_filename=dest_filename
                                                ))
        except:
            safe = False
            while self.attempt_backup_connect():
                try:
                    self.stub.Move(file_pb2.MoveRequest(
                                        old_src=old_src, 
                                        dest_src=dest_src,
                                        dest_filepath=dest_filepath,
                                        dest_filename=dest_filename
                                    ))
                    safe = True
                    break
                except:
                    continue
            if not safe:
                print("FATAL ERROR, ALL SERVERS UNREACHABLE")
                os._exit(FAILURE)

    # Function fires on creation of file or folder
    def on_created(self, event):

        # Give time to detect deletion (check for MOVE events)
        time.sleep(0.1)

        # If we have a file creation, two cases:
        # Case 1: file is a move (object in move_queue)
        try:
            old_src = self.move_queue.get(block=False)

        # Case 2: file is new creation (nothing in move_queue)
        except:
            # New file creation: treat like any modification of a file
            self.on_modified(event)
            return
        
        # Otherwise we might have a file move
        # Extract deleted filename
        _, deleted = os.path.split(old_src)

        # Get creation information
        old_src = old_src.replace("\\", "/")
        dest_src = event.src_path.replace("\\", "/")
        dest_filepath, dest_filename = os.path.split(event.src_path)
        dest_filepath = dest_filepath.replace("\\", "/")

        # Check if files had same name, if so, a move!
        if (deleted == dest_filename):
            self.safe_move(old_src, dest_src, dest_filepath, dest_filename)
            print(f"File {dest_filename} moved from {old_src} to {dest_src}")
        
        # Else it was just a creation again
        else:
            self.on_modified(event)

    # Function fired on file deletion
    def on_deleted(self, event):
        # Put in queue to check for MOVE
        # delete can be triggered by MOVE or DELETE
        # Check for creation to check for MOVE
        self.move_queue.put(event.src_path)
        thread = threading.Thread(target = self.force_delete, args = (), daemon=True)
        thread.start()

    # Empty the move queue after small amount of time
    # To ensure move triggers only when appropriate
    def force_delete(self):
        time.sleep(0.3)
        try:
            self.move_queue.get(block=False)
        except:
            pass
        return

    # Function fires on file RENAMING (NOTE: watchdog method name VERY MISLEADING HERE)
    def on_moved(self, event):
        old_src = event.src_path.replace("\\", "/")
        dest_src = event.dest_path.replace("\\", "/")
        dest_filepath, dest_filename = os.path.split(dest_src)
        dest_filepath.replace("\\", "/")
        self.safe_move(old_src, dest_src, dest_filepath, dest_filename)

    # Push local change to server
    def __push(self, path):
        print(f"\nLocal modification detected at {path}.")
        logging.info(f"Local modification detected at {path}.")

        # We hash the file
        hash = hash_file(path)

        # Get MAC address
        MAC_addr = literal_eval(hex(uuid.getnode() + MAC_DEMO))

        # Process the event source path
        filepath, filename = os.path.split(path)
        safe_filepath = filepath.replace("\\", "/")

        # We check the file to see if it is the same as on the server (no action needed)
        request = file_pb2.CheckRequest(user=self.user_token, hash=hash, clock=self.client_clock)
        response = self.stub.Check(request)

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
            with open(path, "rb") as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    send_queue.put(file_pb2.UploadRequest(file=data))

            # Add sentinel to mark stream termination
            send_queue.put(None)

            # Send grpc request
            response = self.stub.Upload(iter(send_queue.get, None))

            # If success, print result
            if response.status == SUCCESS:
                print(f"Local modification at {path} uploaded to server successfully.")
                logging.info(f"Push to server for {path} complete.")
        return

    def on_modified(self, event):

        # Dodging double detection issue
        statbuf = os.stat(event.src_path)
        new = statbuf.st_mtime

        # Need to avoid getting this on directories (don't add to database for new folders etc)
        if event.is_directory:
            return

        # By checking if the two events were separated by a small delta time, if not, return
        if (new - self.old < self.delta):
            return

        # Otherwise, update last update time
        self.old = new

        # Push modification to server
        try:
            self.__push(event.src_path)
        except:
            safe = False
            while self.attempt_backup_connect():
                try: 
                    self.__push(event.src_path)
                    safe = True
                    break
                except:
                    continue
            if not safe:
                print("FATAL ERROR, ALL SERVERS UNREACHABLE 1")
                os._exit(FAILURE)
        return

# Main class for command processing
class Client:
    def __init__(self, host=HOST_IP, port=PORT):

        # Server info
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.server_online = False

        # User info
        self.user_token = ""
        
        # Backup info
        self.backups = []

    # Attempt to connect to a backup server
    def attempt_backup_connect(self):

        # If out of backups, return False
        if not self.backups:
            return False
        
        # Else get next backup to try
        backup = self.backups.pop()

        # Set host and port to new settings
        self.host = backup.host
        self.port = backup.port

        # Update the channel, closing the previous
        self.channel.close()
        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.stub = file_pb2_grpc.ClientHandlerStub(self.channel)
        return True

    # Attempt to setup backups when connecting to a server
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

    # Valid username check function
    def __valid_username(self, user):
        return user and len(user) < MAX_USERNAME_LENGTH and user.isalnum()

    # Attempt to login
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

    # Log user out
    def attempt_logout(self):
        self.user_token = ""
        return

    # List files user owns
    def attempt_list(self):
        response = self.stub.List(file_pb2.ListRequest(user=self.user_token))

        # if failed, print failure and return
        if response.status == FAILURE:
            print(f"List users error: {response.errormessage}")
            return

        # if success, print filenames in response
        if response.files:
            print(f"Files available to you:")
            for file in response.files:
                print(file)
        else:
            print("You have no files available.")
        return

    # Drop a file from user's tracking so they can delete permanently
    def attempt_drop(self, arg):
        filename = ''.join(arg.split())
        if not filename:
            print("Drop file error: no argument provided.")
            return

        response = self.stub.Drop(file_pb2.DropRequest(user=self.user_token, filename=filename))

        # if failed, print failure and return
        if response.status == FAILURE:
            print(f"Drop file error: {response.errormessage}")
            return

        # if success, print confirmation
        print(f"Dropped {filename} successfully.")
        return

    # Delete user
    def attempt_delete(self):
        self.stub.Delete(file_pb2.DeleteRequest(user=self.user_token))
        self.user_token = ""
        return

    # Feedback on invalid command
    def handle_invalid_command(self, command):
        print(f"Invalid command: {command}, please try \\help for list of commands")

    # Help function to display commands
    def display_command_help(self):
        print(
        """
              -- Valid commands --
        \\help -> provides the text you're seeing now
        \\list -> lists files you have access to
        \\drop filename -> deletes file from server with name 'filename'
        \\logout -> logs you out of your account
        \\delete -> deletes all of your files from server, logs you out
        \\quit -> exits the program
        """
            )

    # General function to process available commands
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
        if command[0:5] == "\\drop":
            self.attempt_drop(command[5:])
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

    # Client Handler service
    def ClientHandler(self, testing=False):

        # Create stub
        self.stub = file_pb2_grpc.ClientHandlerStub(self.channel)

        # Setup condition variable: should only listen when logged in
        condition = threading.Condition()

        # try to setup backups
        self.attempt_setup_backups()

        # For testing only
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

            # If the server is already offline, we have to shutdown
            if not self.server_online:
                observer.shutdown()
                observer.stop()
                logging.error("Server not online.")
                self.shutdown(FAILURE)
            try:
                # Otherwise, main logic loop
                if self.user_token:

                    # If logged in, process commands
                    command = input(f"{self.user_token} > ")

                    # if \quit is run, quit
                    if not self.process_command(command):
                        logging.warning("Quitting...")
                        self.shutdown(SUCCESS)
                else:
                    
                    # Else, attempt login
                    self.attempt_login(condition)
                    logging.info(f"Logged in as {self.user_token}.")

                    # after logging in, begin observer thread
                    event_handler = EventWatcher(self.stub, self.user_token, self.host, self.port, grpc.insecure_channel(self.host + ":" + self.port), self.backups.copy())
                    observer = Observer()
                    observer.schedule(event_handler, path, recursive=True)
                    observer.start()
                    logging.info("Observer thread up.")
            
            # User shutdown from CTRL-C interrupt
            except KeyboardInterrupt:  
                # Shutdown the connections nicely, then stop the thread
                observer.shutdown()
                observer.stop()
                logging.warning("Keyboard interrupt.")

                # Logout and shutdown main thread
                self.attempt_logout()
                self.shutdown(SUCCESS)
            
            # Otherwise likely server has gone down
            except Exception as e:
                
                # Attempt to connect to backups
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
                
                # If all failed, no choice but to shutdown
                if not safe:
                    logging.error(e)
                    self.shutdown(FAILURE)
        observer.join()

    # Helper to store file locally
    def __store_file(self, r, filepath, filename, MAC, local_MAC, data):
        
        # Create folders if necessary
        path = os.path.abspath(filepath)
        os.makedirs(path, exist_ok=True)

        # Rename file if local version ahead of latest version from server
        # The 'OneDrive' solution we talked about
        src = os.path.join(filepath, filename)
        if os.path.isfile(src) and MAC != local_MAC:
            os.rename(src, os.path.join(filepath, str(local_MAC) + "_" + filename)) 
        
        # Write in the binary data
        with open(src, "wb") as f:
            f.write(data)

    def __pull(self):

        # First building metadata of local files
        local_files = [os.path.join(dirpath,f).replace("\\", "/") for (dirpath, dirnames, filenames) in os.walk(FILE_PATH) for f in filenames]
        request = file_pb2.SyncRequest(user=self.user_token)
        MAC_addr = literal_eval(hex(uuid.getnode()))

        # Send metadata of each to server to compare
        for file in local_files:
            filepath, filename = os.path.split(file)
            request.metadata.append(file_pb2.Metadata(clock=0,
                                                        user=self.user_token,
                                                        hash=hash_file(file),
                                                        MAC=MAC_addr,
                                                        filename=filename,
                                                        filepath=filepath))
        
        # Get responses
        responses = self.stub.Sync(request)

        # Setup variables
        data = bytearray()
        file_received = False
        filename = None
        filepath = None
        local_MAC = literal_eval(hex(uuid.getnode()))

        # Pull data
        for r in responses:
            if r.HasField("will_receive"):
                break
            else:
                try:
                    if r.HasField("meta"):
                        if file_received:
                            self.__store_file(r, filepath, filename, MAC, local_MAC, data)
                            data = bytearray()
                        filename = r.meta.filename
                        filepath = r.meta.filepath
                        MAC = r.meta.MAC
                        file_received = True
                        print(f"Successful sync at {r.meta.filepath}/{r.meta.filename}.")
                    else:
                        data.extend(r.file)
                except Exception as e:
                    logging.error(e)

        # Catch last file
        try:
            if file_received:
                self.__store_file(r, filepath, filename, MAC, local_MAC, data)
                data = bytearray()
            print(f"Successful sync at {r.meta.filepath}/{r.meta.filename}.")
        except Exception as e:
            logging.error(e)

    # Listener to listen from the server
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
                        logging.error("Test")
                        logging.error(e)
                        self.shutdown(FAILURE)
                sleep(SYNC_RATE)
            else:
                with condition:
                    condition.wait()

    # Shutdown main thread nicely
    def shutdown(self, status):
        self.channel.close()
        print("Goodbye!")
        logging.warning("Shutting down.")
        os._exit(status)

    # Main run loop
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
