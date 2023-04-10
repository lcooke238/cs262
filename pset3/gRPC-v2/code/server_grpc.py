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

# TODO: Remove temporary Empty object type
EMPTY = chat_pb2.Empty()

# ADJUSTABLE PARAMETERS BELOW:

# set to true to wipe messages/users database on next run
RESET_DB = True

# set server address
BASE_PORT = 50051


class ClientHandler(chat_pb2_grpc.ClientHandlerServicer):
    def __init__(self, state, backups):
        self.state = state
        self.backups = backups
        print(self.backups)

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
                    # Adding user on this server
                    cur.execute("INSERT INTO users (user, online) VALUES (?, ?)",
                                (request.user, True))
                    con.commit()

                    # Adding user to other backups
                    worker = ServerWorker(self.backups)
                    worker.adduser(request.user)

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

                    worker = ServerWorker(self.backups)
                    worker.setuserstatus(request.user, False)

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
                    worker = ServerWorker(self.backups)
                    worker.removeuser(request.user)

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

                # Send message on backups
                worker = ServerWorker(self.backups)
                worker.send(request.user, request.message, request.target)

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

                worker = ServerWorker(self.backups)
                worker.deletemessages(request.user)

                return unread_message_packet

    def DeleteMessages(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM messages WHERE recipient = ?",
                            (request.user, ))
                con.commit()
        return EMPTY

    def AddMessage(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)",
                            (request.user, request.message, request.target, ))
                con.commit()
        return EMPTY

    def SetUserStatus(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("UPDATE users SET online = ? WHERE user = ?",
                            (request.status, request.user, ))
                con.commit()
        return EMPTY

    def AddUser(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (user, online) VALUES (?, ?)",
                            (request.user, True))
                con.commit()
        return EMPTY

    def RemoveUser(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM users WHERE user = ?",
                            (request.user, ))
                con.commit()
        return EMPTY

class ServerWorker():
    def __init__(self, backups):
        self.backups = backups
    
    def send(self, sender, message, recipient):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = chat_pb2_grpc.ClientHandlerStub(channel)
                stub.AddMessage(chat_pb2.SendRequest(user=sender, message=message, target=recipient))
                channel.close()
            except:
                continue

    def adduser(self, user):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = chat_pb2_grpc.ClientHandlerStub(channel)
                stub.AddUser(chat_pb2.LoginRequest(user=user))
                channel.close()
            except Exception as e:
                print(e)
                continue
    
    def removeuser(self, user):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = chat_pb2_grpc.ClientHandlerStub(channel)
                stub.RemoveUser(chat_pb2.DeleteRequest(user=user))
                channel.close()
            except Exception as e:
                print(e)
                continue
    
    def deletemessages(self, user):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = chat_pb2_grpc.ClientHandlerStub(channel)
                stub.DeleteMessages(chat_pb2.GetRequest(user=user))
                channel.close()
            except Exception as e:
                print(e)
                continue
    
    def setuserstatus(self, user, status):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = chat_pb2_grpc.ClientHandlerStub(channel)
                stub.SetUserStatus(chat_pb2.SetStatusRequest(user=user, status=status))
                channel.close()
            except Exception as e:
                print(e)
                continue

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
    global DATABASE_PATH

    # Give the server an id
    while True:
        id_input = input("Give this server an id (0-100): ")
        try:
            id = int(id_input)
            if (id <= 100 and id >= 0):
                # Currently for internal testing we need a separate database for each server
                DATABASE_PATH = f"../data/data_{id}.db"
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
        # TODO: Fix all this stuff being specific to running internal servers
        if int(backup_port) > BASE_PORT + id:
            backups.append({"host": backup_host, "port": backup_port})
    backups.reverse()
    return state, id, backups

# runs the server logic
def serve(mode):
    # initialize logs
    logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

    if mode == ServerMode.INTERNAL:
        host = "[::]"
    else:
        hostname = socket.gethostname()   
        host = socket.gethostbyname(hostname)

    state, id, backups = setup()
    port = str(BASE_PORT + id)

    # initialize database
    init_db()

    # handling any weird crashes to ensure users can still log in
    set_all_offline()

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
