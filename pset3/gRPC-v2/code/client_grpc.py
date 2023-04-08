import logging
import threading
import grpc
import chat_pb2
import chat_pb2_grpc
import sys
import os

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


class Client:

    def __init__(self, host=HOST_IP, port=PORT):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.user_token = ""
        self.backups = []
        self.server_online = False

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
        self.stub = chat_pb2_grpc.ClientHandlerStub(self.channel)
        return True

    def attempt_setup_backups(self):
        response = self.stub.GetBackups(chat_pb2.BackupRequest())
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
        response = self.stub.Login(chat_pb2.LoginRequest(user=user))

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

    def attempt_list(self, args):
        response = self.stub.ListUsers(chat_pb2.ListRequest(args=args))

        # if failed, print failure and return
        if response.status == FAILURE:
            print(f"List users error: {response.errormessage}")
            return

        # if success, print users that match the wildcard provided
        print(f"Users matching wildcard {response.wildcard}:")
        for user in response.user:
            print(user)

    def attempt_logout(self):
        response = self.stub.Logout(chat_pb2.LogoutRequest(user=self.user_token))
        if response.status == FAILURE:
            print(f"Logout error: {response.errormessage}")
            return
        self.user_token = ""

    def attempt_delete(self):
        self.stub.Delete(chat_pb2.DeleteRequest(user=self.user_token))
        self.user_token = ""

    def attempt_send(self, args):
        arg_list = [arg.strip() for arg in args.split("->")]
        if len(arg_list) != 2:
            print("Invalid message send syntax. Correct syntax: \\send {message} -> {user}")
            return

        if not self.__valid_username(arg_list[1]):
            print(f"Username provided is invalid: {arg_list[1]}. All usernames are alphanumeric")
            return

        if len(arg_list[0]) > MAX_MESSAGE_LENGTH:
            print(f"Message length capped at {MAX_MESSAGE_LENGTH}. Please shorten or send in multiple messages")
            return

        message, target = arg_list[0], arg_list[1]
        response = self.stub.Send(chat_pb2.SendRequest(user=self.user_token,
                                                       message=message,
                                                       target=target))
        if response.status == FAILURE:
            print(f"Send message error: {response.errormessage}")

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
        safe = False
        try:
            if len(command) < 5:
                self.handle_invalid_command(command)
                return True
            if command[0:5] == "\\help":
                self.display_command_help()
                return True
            if command[0:5] == "\\list":
                self.attempt_list(command[5:])
                return True
            if command[0:5] == "\\send":
                self.attempt_send(command[5:])
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
        except:
            while self.attempt_backup_connect():
                try:
                    self.process_command(command)
                    safe = True
                    break
                except:
                    continue
            if not safe:
                self.handle_server_shutdown()
        return True


    def ClientHandler(self, testing=False):
        # Create stub
        self.stub = chat_pb2_grpc.ClientHandlerStub(self.channel)

        # Try to setup backups
        self.attempt_setup_backups()

        condition = threading.Condition()

        if testing:
            self.attempt_login(condition)
            return

        # start new Daemon thread listening for messages with condition variable
        # to sync with main thread to have blocking rather than polling
        thread = threading.Thread(target=self.listen, args=(condition,))
        thread.daemon = True
        thread.start()
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
                    try:
                        self.attempt_login(condition)
                    except:
                        # TODO: Fix this safe condition, not sure what's going on here right now
                        safe = True
                        while self.attempt_backup_connect():
                            try:
                                self.process_command(command)
                                safe = True
                                break
                            except:
                                continue
                        if not safe:
                            self.handle_server_shutdown()
            except KeyboardInterrupt:  # for ctrl-c interrupt
                self.attempt_logout()
                self.channel.close()
                print("Logging you out!")
                break

    def listen(self, condition):
        while True:
            if self.user_token:
                try:
                    response = self.stub.GetMessages(chat_pb2.GetRequest(user=self.user_token))
                except:
                    continue
                if response.status == SUCCESS_WITH_DATA:
                    print("")
                    for message in response.message:
                        print(f"\033[94m{message.sender} > \033[0m{message.message}")
                    print(f"{self.user_token} > ", end="")
            else:
                with condition:
                    condition.wait()

    def handle_server_shutdown(self):
        print("Shutting down!")
        self.channel.close()
        os._exit(FAILURE)

    def run(self, testing=False):
        # initialize logs
        logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

        self.channel = grpc.insecure_channel(self.host + ":" + self.port)
        self.server_online = True
        self.ClientHandler(testing)


if __name__ == '__main__':
    client = Client()
    client.run()
