from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc
import threading
from collections import defaultdict
import sqlite3

# 3 uses serialized mode - can be used safely by multiple threads with no restriction
# Documentation/ and only answers seem to differ about this, so implementing a lock anyway
sqlite3.threadsafety = 3

lock = threading.Lock()

DATABASE_PATH = "../data/data.db"

sqlite_connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
db_cursor = sqlite_connection.cursor()

SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

NO_ERROR = ""

# Playing with state
storage = {}
users = ["andrew", "ben"]
logged_in_users = ["ben"]
unread_messages = defaultdict(list)
unread_messages["andrew"].append("ben > Hey Andrew")
unread_messages["andrew"].append("andrew > Note to self: turn this into db")
counter = 0

class ClientHandler(chat_pb2_grpc.ClientHandlerServicer):
    def Login(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                logged_in = cursor.execute("SELECT online FROM users WHERE user=?", (request.user, )).fetchall()
                print(logged_in)
                if not logged_in:
                    cursor.execute("INSERT INTO users (user, online) VALUES (?, ?)", (request.user, True))
                    con.commit()
                    return chat_pb2.LoginReply(status = SUCCESS, errormessage=NO_ERROR, user=request.user)
                if logged_in[0][0]:
                    return chat_pb2.LoginReply(status=FAILURE, errormessage="User already logged in on different machine", user=request.user)
                else:
                    cursor.execute("UPDATE users SET online = ? WHERE user = ?", (True, request.user, ))
                    con.commit()
                    return chat_pb2.LoginReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)
        
    def Logout(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                logged_in = cursor.execute("SELECT user FROM users WHERE user = ?", (request.user, )).fetchall()
                if logged_in and logged_in[0]:
                    cursor.execute("UPDATE users SET online = FALSE WHERE user = ?", (request.user, ))
                    con.commit()
                    return chat_pb2.LogoutReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)
                return chat_pb2.LogoutReply(status=FAILURE, errormessage="User not currently logged in", user=request.user)
    
    def Delete(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                logged_in = cursor.execute("SELECT online FROM users WHERE user = ?", (request.user, )).fetchall()
                if logged_in:
                    cursor.execute("DELETE FROM users WHERE user = ?", (request.user, ))
                    con.commit()
                return chat_pb2.DeleteReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)

    def ListUsers(self, request, context):
        wildcard = request.args.strip()
        with sqlite3.connect(DATABASE_PATH) as con:
            # Basic wildcard, is user equal to a user in the list, or is it *
            cursor = con.cursor()
            user_list = chat_pb2.ListReply(status=SUCCESS, wildcard=wildcard, errormessage="")
            matched_users = cursor.execute("SELECT user FROM users WHERE user LIKE ?", (wildcard, )).fetchall()
            print(matched_users)
            for user in matched_users:
                user_list.user.append(user[0])
            return user_list

    def Send(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                if request.target not in users:
                    return chat_pb2.SendReply(status=FAILURE, errormessage="User does not exist :(", user=request.user, message="[]", target=request.target)
                unread_messages[request.target].append(request.message)
                print(unread_messages)
                if request.target not in logged_in_users:
                    return chat_pb2.SendReply(status=SUCCESS, errormessage="User offline, message will be received upon login", user=request.user, message="[]", target=request.target)
                return chat_pb2.SendReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user, message="[]", target=request.target) 

    def GetMessages(self, request, context):
        if request.user not in users:
            return chat_pb2.GetReply(status=FAILURE, errormessage="User does not exist :(")
        status = SUCCESS_WITH_DATA if len(unread_messages[request.user]) else SUCCESS
        unread_message_packet = chat_pb2.GetReply(status=status, errormessage=NO_ERROR)
        while len(unread_messages[request.user]) > 0:
            message = unread_messages[request.user].pop(False)
            single_message = chat_pb2.UnreadMessage(sender="UNKNOWN/NOT IMPLEMENTED", message=message, receiver=request.user)
            unread_message_packet.message.append(single_message)
        return unread_message_packet



def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        sqlite_connection.close()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
