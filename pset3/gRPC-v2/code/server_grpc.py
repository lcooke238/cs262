from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc
import threading
import sqlite3
from enum import Enum
import socket

# 3 uses serialized mode - can be used safely by multiple threads with no restriction
# Documentation/ and only answers seem to differ about this, so implementing a lock anyway
sqlite3.threadsafety = 3

lock = threading.Lock()

LOG_PATH = "../logs/server_grpc.log"
DATABASE_PATH = "../data/data.db"

# statuses
SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2
FAILURE_WITH_DATA = 3

# error messages
NO_ERROR = ""
ERROR_DIFF_MACHINE = "user already logged in on different machine"
ERROR_NOT_LOGGED_IN = "user not currently logged in"
ERROR_DNE = "user does not exist :("

# ADJUSTABLE PARAMETERS BELOW:

# set to true to wipe messages/users database on next run
RESET_DB = True

# set server address
BASE_PORT = 50051


class ClientHandler(chat_pb2_grpc.ClientHandlerServicer):
    def __init__(self, state, backups):
        self.state = state
        self.backups = backups

    def GetBackups(self, request, context):
        response = chat_pb2.BackupReply(status=0, errormessage="")
        for backup in self.backups:
            response.serverinfo.append(chat_pb2.ServerInfo(host=backup["host"], port=backup["port"]))
        return response

    # def CreateBackupChain(self, request, context):
    #     # Add this server to the chain of backups
    #     thisinfo = chat_pb2.ServerInfo(host=self.host, port=self.port)
    #     serverinfo = request.serverinfo
    #     serverinfo.append(thisinfo)

    #     # If end of the chain, return the chain
    #     if not(self.backup_host and self.backup_port):
    #         if len(request.serverinfo > request.number_backups):
    #             status = SUCCESS
    #         elif len(request.serverinfo):
    #             status = FAILURE_WITH_DATA
    #         else:
    #             status = FAILURE
    #         return chat_pb2.BackupReply(status=status, errormessage="", serverinfo=serverinfo)
        
    #     # If not end of the chain, pull from up the chain
    #     channel = grpc.insecure_channel(self.backup_host + ":" + self.backup_port)
    #     stub = chat_pb2_grpc.ClientHandlerStub(channel)
    #     rq = chat_pb2.BackupRequest(number_backups=request.number_backups, serverinfo=serverinfo)
    #     response = stub.CreateBackupChain(rq)
    #     channel.close()
    #     return response

    # logs a user in
    def Login(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # check whether already logged in
                logged_in = cur.execute("SELECT online FROM users WHERE user = ?",
                                        (request.user,)).fetchall()

                # user doesn't exist (returned empty list)
                if not logged_in:
                    cur.execute("INSERT INTO users (user, online) VALUES (?, ?)",
                                (request.user, True))
                    con.commit()
                    return chat_pb2.LoginReply(status=SUCCESS,
                                               errormessage=NO_ERROR,
                                               user=request.user)

                # currently logged in
                if logged_in[0][0]:
                    return chat_pb2.LoginReply(status=FAILURE,
                                               errormessage=ERROR_DIFF_MACHINE,
                                               user=request.user)

                # user exists but not currently logged in
                else:
                    cur.execute("UPDATE users SET online = ? WHERE user = ?",
                                (True, request.user,))
                    con.commit()
                    return chat_pb2.LoginReply(status=SUCCESS,
                                               errormessage=NO_ERROR,
                                               user=request.user)

    # logs a user out
    def Logout(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # they should be logged in to be able to run this,
                # but just checking to avoid errors
                logged_in = cur.execute("SELECT user FROM users WHERE user = ?",
                                        (request.user, )).fetchall()

                if logged_in and logged_in[0]:
                    cur.execute("UPDATE users SET online = FALSE WHERE user = ?",
                                (request.user, ))
                    con.commit()
                    return chat_pb2.LogoutReply(status=SUCCESS,
                                                errormessage=NO_ERROR,
                                                user=request.user)

                return chat_pb2.LogoutReply(status=FAILURE,
                                            errormessage=ERROR_NOT_LOGGED_IN,
                                            user=request.user)

    # deletes a user from the database
    def Delete(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # they should be logged in to be able to run this,
                # but just checking to avoid errors
                logged_in = cur.execute("SELECT online FROM users WHERE user = ?",
                                        (request.user, )).fetchall()

                if logged_in:
                    cur.execute("DELETE FROM users WHERE user = ?",
                                (request.user, ))
                    con.commit()

                return chat_pb2.DeleteReply(status=SUCCESS,
                                            errormessage=NO_ERROR,
                                            user=request.user)

    # Lists users in the database using SQL wildcard syntax
    def ListUsers(self, request, context):
        wildcard = request.args.strip()
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()

            # no real way for this to fail so just set as SUCCESS
            user_list = chat_pb2.ListReply(status=SUCCESS,
                                           wildcard=wildcard,
                                           errormessage="")

            # pull users according to SQL wildcard
            matched_users = cur.execute("SELECT user FROM users WHERE user LIKE ?",
                                        (wildcard, )).fetchall()
            for user in matched_users:
                user_list.user.append(user[0])

            return user_list

    # sends a message from one client to another
    def Send(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # check whether the name they gave to send to is valid user
                target_check = cur.execute("SELECT user FROM users WHERE user = ?",
                                           (request.user, ))
                if not target_check:
                    return chat_pb2.SendReply(status=FAILURE,
                                              errormessage=ERROR_DNE,
                                              user=request.user,
                                              message=request.message,
                                              target=request.target)

                # put message into database
                cur.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)",
                            (request.user, request.message, request.target, ))
                con.commit()
                return chat_pb2.SendReply(status=SUCCESS,
                                          errormessage=NO_ERROR,
                                          user=request.user,
                                          message=request.message,
                                          target=request.target)

    # pulls messages from server to client
    def GetMessages(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # checking for an error;
                # they should be logged in to be running this command
                user_check = cur.execute("SELECT online FROM users WHERE user = ?",
                                         (request.user, )).fetchall()
                if not user_check or not user_check[0][0]:
                    return chat_pb2.GetReply(status=FAILURE,
                                             errormessage=ERROR_DNE)

                # pull unread messages;
                # set return status depending on presence of unread messages
                unread_messages = cur.execute("SELECT * FROM messages WHERE recipient = ?",
                                              (request.user, )).fetchall()
                status = SUCCESS_WITH_DATA if unread_messages else SUCCESS

                # add all unread messages to a packet
                unread_message_packet = chat_pb2.GetReply(status=status,
                                                          errormessage=NO_ERROR)
                for unread in unread_messages:
                    single_message = chat_pb2.UnreadMessage(sender=unread[1],
                                                            message=unread[2],
                                                            receiver=request.user)
                    unread_message_packet.message.append(single_message)

                # remove those messages from the unread database;
                # note that we had the lock, so no new messages
                # could have arrived during this time
                cur.execute("DELETE FROM messages WHERE recipient = ?",
                            (request.user, ))
                con.commit()

                return unread_message_packet

    def DeleteMessages(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM messages WHERE recipient = ?",
                            (request.user, ))
                con.commit()

    def AddMessage(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)",
                            (request.user, request.message, request.target, ))
                con.commit()

    def setUserStatus(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("UPDATE users SET online = ? WHERE user = ?",
                            (request.status, request.user, ))
                con.commit()

    def AddUser(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (user, online) VALUES (?, ?)",
                            (request.user, True))
                con.commit()

    def RemoveUse(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM users WHERE user = ?",
                            (request.user, ))
                con.commit()

class ServerStatus(Enum):
    SETUP = 0
    LEADER = 1
    FOLLOWER = 2
    ERROR = 3

class Server():
    def __init__(self, host="127.0.0.1", port="50051"):
        self.state = ServerStatus.SETUP
        self.client_handler = None 
        self.backup_host = None
        self.backup_port = None
        self.host = host
        self.port = port
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname)   
    
    # Must be called before using any other method
    def setup(self):
        while True:
            role = input("Role of this server: ")
            match role:
                case "leader":
                    self.state = ServerStatus.LEADER
                    break
                case "follower":
                    self.state = ServerStatus.FOLLOWER
                    break
            print("Invalid role entered. Valid options: leader, follower.")
        # Currently not needed
        while True:
            self.backup_host = input("Backup Server IP:  (hit enter if none)")
            self.backup_port = input("Backup server host: (hit enter if none)")
            if self.backup_host and self.backup_port:
                self.client_handler = ClientHandler(self.backup_host, self.backup_port)
            else:
                print("WARNING: this server has no backups")
                self.client_handler = ClientHandler(None, None)
            break

    # takes the lock and sets all users offline
    def set_all_offline(self):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("UPDATE users SET online = FALSE")
                con.commit()

    # initializes database
    def init_db(self):
        con = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        cur = con.cursor()

        # create database if necessary
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                        user VARCHAR(100) PRIMARY KEY,
                        online BOOL
                    )""")
        con.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS messages (
                        message_id INTEGER PRIMARY KEY,
                        sender VARCHAR(100),
                        message VARCHAR(10000),
                        recipient VARCHAR(100)
                    )""")
        con.commit()

        # clear database if desired
        if RESET_DB:
            cur.execute("DELETE FROM users")
            con.commit()
            cur.execute("DELETE FROM messages")
            con.commit()

    def serve(self):
        # Ensure setup is run by running it yourself
        self.setup()
        # initialize logs
        logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

        # handling any weird crashes to ensure users can still log in
        self.set_all_offline()

        # initialize database
        self.init_db()

        # run server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_ClientHandlerServicer_to_server(self.client_handler, server)
        server.add_insecure_port('[::]:' + self.port)
        server.start()
        print("server started, listening on " + self.host + self.port)

        # shut down nicely
        try:
            server.wait_for_termination()
            self.set_all_offline()
        except KeyboardInterrupt:
            self.set_all_offline()


# takes the lock and sets all users offline
def set_all_offline():
    with lock:
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET online = FALSE")
            con.commit()


# initializes database
def init_db():
    con = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cur = con.cursor()

    # create database if necessary
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                       user VARCHAR(100) PRIMARY KEY,
                       online BOOL
                   )""")
    con.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
                       message_id INTEGER PRIMARY KEY,
                       sender VARCHAR(100),
                       message VARCHAR(10000),
                       recipient VARCHAR(100)
                   )""")
    con.commit()

    # clear database if desired
    if RESET_DB:
        cur.execute("DELETE FROM users")
        con.commit()
        cur.execute("DELETE FROM messages")
        con.commit()

class ServerMode(Enum):
    INTERNAL = 0
    EXTERNAL = 1

# Call to set up backups
def setup():

    # Setting up leader/follower roles
    # while True:
    #     role = input("Role of this server: ")
    #     match role:
    #         case "leader":
    #             state = ServerStatus.LEADER
    #             break
    #         case "follower":
    #             state = ServerStatus.FOLLOWER
    #             break
    #     print("Invalid role entered. Valid options: leader, follower.")
    state = ServerStatus.LEADER

    # Give the server an id
    while True:
        id_input = input("Give this server an id (0-100): ")
        try:
            id = int(id_input)
            if (id <= 100 and id >= 0):
                break
        except:
            print("Provide a numerical input between 0 and 100 inclusive!")

    # Get number of backups
    while True:
        num_backups_input = input("Number of backup servers?: ")
        try:
            num_backups = int(num_backups_input)
            if (0 <= num_backups and num_backups <= 10):
                break
        except:
            print("Provide a numerical input between 0 and 10 inclusive!")

    # Setting up backups
    backups = []
    for i in range(num_backups):
        while True:
            try:
                backup_host = input(f"Backup Server #{i + 1} IP (default 127.0.0.1): ")
                backup_id = input(f"Backup Server #{i + 1} ID: ")
                if not backup_host:
                    backup_host = "127.0.0.1"
                backup_port = int(backup_id) + BASE_PORT
                if (BASE_PORT <= backup_port and backup_port <= BASE_PORT + 100):
                    backup_port = str(backup_port)
                    break
            except:
                print("Provide a numerical input for backup ID between 0 and 100 inclusive!")
        backups.append({"host": backup_host, "port": backup_port})

    return state, id, backups

# runs the server logic
def serve(mode):
    # initialize logs
    logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

    # handling any weird crashes to ensure users can still log in
    set_all_offline()

    # initialize database
    init_db()

    if mode == ServerMode.INTERNAL:
        host = "[::]"
    else:
        hostname = socket.gethostname()   
        host = socket.gethostbyname(hostname)

    state, id, backups = setup()
    port = str(BASE_PORT + id)

    # run server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(state, backups), server)
    server.add_insecure_port(host + ":" + port)
    server.start()
    print("server started, listening on " + host + ":" + port)

    # shut down nicely
    try:
        server.wait_for_termination()
        set_all_offline()
    except KeyboardInterrupt:
        set_all_offline()


if __name__ == '__main__':
    serve(ServerMode.INTERNAL)


# ================= RADIOACTIVE FALLOUT ZONE =================


# class SimulatedClient:
#     # Should initialize simulated client with host=backup_host, port=backup_port -> we want to connect to our next backup!
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.channel = None
#         self.stub = None
#         self.user_token = ""
#         self.server_online = False
#
#     # Simulated clients will always be given valid parameters
#     def attempt_login(self, condition):
#         # attempt login on server
#         try:
#             response = self.stub.Login(chat_pb2.LoginRequest(user=user))
#         except:
#             self.handle_server_shutdown()
#
#         # if failure, print failure and return; they can attempt again
#         if response.status == FAILURE:
#             print(f"Login error: {response.errormessage}")
#             return
#
#         # if success, set user token and print success
#         self.user_token = response.user
#
#         # notify listener thread to start listening
#         with condition:
#             condition.notify_all()
#
#     def attempt_list(self, args):
#         # attempt to retrieve user list from server
#         try:
#             response = self.stub.ListUsers(chat_pb2.ListRequest(args=args))
#         except:
#             self.handle_server_shutdown()
#
#         # if failed, print failure and return
#         if response.status == FAILURE:
#             print(f"List users error: {response.errormessage}")
#             return
#
#         # if success, print users that match the wildcard provided
#         print(f"Users matching wildcard {response.wildcard}:")
#         for user in response.user:
#             print(user)
#
#     def attempt_logout(self):
#         try:
#             response = self.stub.Logout(chat_pb2.LogoutRequest(user=self.user_token))
#         except:
#             self.handle_server_shutdown()
#         if response.status == FAILURE:
#             print(f"Logout error: {response.errormessage}")
#             return
#         self.user_token = ""
#         return
#
#     def attempt_delete(self):
#         try:
#             self.stub.Delete(chat_pb2.DeleteRequest(user=self.user_token))
#         except:
#             self.handle_server_shutdown()
#         self.user_token = ""
#         return
#
#     def attempt_send(self, args):
#         arg_list = [arg.strip() for arg in args.split("->")]
#         if len(arg_list) != 2:
#             print("Invalid message send syntax. Correct syntax: \\send {message} -> {user}")
#             return
#
#         if not self.__valid_username(arg_list[1]):
#             print(f"Username provided is invalid: {arg_list[1]}. All usernames are alphanumeric")
#             return
#
#         if len(arg_list[0]) > MAX_MESSAGE_LENGTH:
#             print(f"Message length capped at {MAX_MESSAGE_LENGTH}. Please shorten or send in multiple messages")
#             return
#
#         message, target = arg_list[0], arg_list[1]
#         try:
#             response = self.stub.Send(chat_pb2.SendRequest(user=self.user_token,
#                                                 message=message,
#                                                 target=target))
#             if response.status == FAILURE:
#                 print(f"Send message error: {response.errormessage}")
#                 return
#         except:
#             self.handle_server_shutdown()
#
#     def process_command(self, command):
#         if len(command) < 5:
#             self.handle_invalid_command(command)
#             return True
#         if command[0:5] == "\\help":
#             self.display_command_help()
#             return True
#         if command[0:5] == "\\list":
#             self.attempt_list(command[5:])
#             return True
#         if command[0:5] == "\\send":
#             self.attempt_send(command[5:])
#             return True
#         if command[0:5] == "\\quit":
#             self.attempt_logout()
#             return False
#         if len(command) < 7:
#             self.handle_invalid_command(command)
#             return True
#         if command[0:7] == "\\logout":
#             self.attempt_logout()
#             return True
#         if command[0:7] == "\\delete":
#             self.attempt_delete()
#             return True
#         self.handle_invalid_command(command)
#         return True
#
#     def ClientHandler(self, testing=False):
#         self.stub = chat_pb2_grpc.ClientHandlerStub(self.channel)
#         condition = threading.Condition()
#
#         if testing:
#             self.attempt_login(condition)
#             return
#
#         # start new Daemon thread listening for messages with condition variable
#         # to sync with main thread to have blocking rather than polling
#         thread = threading.Thread(target=self.listen, args=(condition,))
#         thread.daemon = True
#         thread.start()
#         while True:
#             if not self.server_online:
#                 self.handle_server_shutdown()
#             try:
#                 if self.user_token:
#                     command = input(f"{self.user_token} > ")
#                     # if \quit is run, quit
#                     if not self.process_command(command):
#                         print("See you later!")
#                         self.channel.close()
#                         break
#                 else:
#                     self.attempt_login(condition)
#             except KeyboardInterrupt:  # for ctrl-c interrupt
#                 self.attempt_logout()
#                 self.channel.close()
#                 print("Logging you out!")
#                 break
#
#     def listen(self, condition):
#         while True:
#             if self.user_token:
#                 try:
#                     response = self.stub.GetMessages(chat_pb2.GetRequest(user=self.user_token))
#                 except:
#                     self.server_online = False
#                     self.handle_server_shutdown()
#                 if response.status == SUCCESS_WITH_DATA:
#                     continue
#             else:
#                 with condition:
#                     condition.wait()
#
#     def handle_server_shutdown(self):
#         self.channel.close()
#         os._exit(FAILURE)
#
#     def run(self, testing=False):
#         # initialize logs
#         logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)
#
#         self.channel = grpc.insecure_channel(self.host + ":" + self.port)
#         self.server_online = True
#         self.ClientHandler(testing)
