import logging
import threading
import grpc
import chat_pb2
import chat_pb2_grpc
import sys

LOG_PATH = "../logs/client_grpc.log"

# statuses
SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2


# customize default server address
DEFAULT_HOST_IP = "localhost"
DEFAULT_PORT = "50051"


class Client:

    def __init__(self, host=DEFAULT_HOST_IP, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.stub = None
        self.user_token = ""
        self.server_online = False

    def attempt_login(self, condition):
        user = input("Please enter a username: ")

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

    def attempt_list(self, args):
        # attempt to retrieve user list from server
        try:
            response = self.stub.ListUsers(chat_pb2.ListRequest(args=args))
        except:
            self.handle_server_shutdown()

        # if failed, print failure and return
        if response.status == FAILURE:
            print(f"List users failed, error: {response.errormessage}")
            return
        # if success, print users that match the wildcard provided
        print(f"Users matching wildcard {response.wildcard}:")
        for user in response.user:
            print(user)

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

    def attempt_send(self, args):
        global user_token
        arg_list = [arg.strip() for arg in args.split("->")]
        if len(arg_list) != 2:
            print("Invalid message send syntax. Correct syntax: \\send {message} -> {user}")
            return

        message, target = arg_list[0], arg_list[1]
        try:
            self.stub.Send(chat_pb2.SendRequest(user=self.user_token,
                                                message=message,
                                                target=target))
        except:
            self.handle_server_shutdown()

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
        return True

    def ClientHandler(self, channel, manual=False):
        self.stub = chat_pb2_grpc.ClientHandlerStub(channel)
        condition = threading.Condition()

        if manual:
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
                        break
                else:
                    self.attempt_login(condition)
            except KeyboardInterrupt:  # for ctrl-c interrupt
                self.attempt_logout()
                print("Logging you out!")
                break

    def listen(self, condition):
        while True:
            if self.user_token:
                try:
                    response = self.stub.GetMessages(chat_pb2.GetRequest(user=self.user_token))
                except:
                    self.server_online = False
                    break
                if response.status == SUCCESS_WITH_DATA:
                    for message in response.message:
                        print(f"{message.sender} > {message.message}")
                    print(f"{self.user_token} > ", end="")
            else:
                with condition:
                    condition.wait()

    def handle_server_shutdown(self):
        print("Error: server error")
        sys.exit()

    def run(self, manual=False):

        # initialize logs
        logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

        with grpc.insecure_channel(self.host + ":" + self.port) as channel:
            self.server_online = True
            self.ClientHandler(channel, manual)


if __name__ == '__main__':
    client = Client()
    client.run()
