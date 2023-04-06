from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc
import threading
import sqlite3
from enum import Enum

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

# error messages
NO_ERROR = ""
ERROR_DIFF_MACHINE = "user already logged in on different machine"
ERROR_NOT_LOGGED_IN = "user not currently logged in"
ERROR_DNE = "user does not exist :("

# ADJUSTABLE PARAMETERS BELOW:

# set to true to wipe messages/users database on next run
RESET_DB = True

# set server address
PORT = "50051"


class ClientHandler(chat_pb2_grpc.ClientHandlerServicer):
    def __init__(self, host, port):
        self.backup_host = host
        self.backup_port = port

    def CreateBackupChain(self, args):
        


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


class ServerStatus(Enum):
    SETUP = 0
    LEADER = 1
    FOLLOWER = 2
    ERROR = 3

class Server():
    def __init__(self):
        self.state = ServerStatus.SETUP
        self.client_handler = None 
        self.backup_host = None
        self.backup_port = None
    
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
        server.add_insecure_port('[::]:' + PORT)
        server.start()
        print("server started, listening on " + PORT)

        # shut down nicely
        try:
            server.wait_for_termination()
            self.set_all_offline()
        except KeyboardInterrupt:
            self.set_all_offline()

if __name__ == '__main__':
    server = Server()
    server.serve()