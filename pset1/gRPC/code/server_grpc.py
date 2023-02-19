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

# Code to wipe the database if you want a fresh copy

# sqlite_connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
# db_cursor = sqlite_connection.cursor()
# db_cursor.execute("DELETE FROM users")
# sqlite_connection.commit()
# db_cursor.execute("DELETE FROM messages")
# sqlite_connection.commit()

SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

NO_ERROR = ""

class ClientHandler(chat_pb2_grpc.ClientHandlerServicer):
    def Login(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                logged_in = cursor.execute("SELECT online FROM users WHERE user=?", (request.user, )).fetchall()
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
                cursor = con.cursor()
                target_check = cursor.execute("SELECT user FROM users WHERE user = ?", (request.user, ))
                if not target_check:
                    return chat_pb2.SendReply(status=FAILURE, errormessage="User does not exist :(", user=request.user, message=request.message, target=request.target)
                cursor.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)", (request.user, request.message, request.target, ))
                con.commit()
                return chat_pb2.SendReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user, message=request.message, target=request.target) 

    def GetMessages(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                user_check = cursor.execute("SELECT online FROM users WHERE user = ?", (request.user, )).fetchall()
                if not user_check or not user_check[0][0]:
                    return chat_pb2.GetReply(status=FAILURE, errormessage="User does not exist :(")
                unread_messages = cursor.execute("SELECT * FROM messages WHERE recipient = ?", (request.user, )).fetchall()
                status = SUCCESS_WITH_DATA if unread_messages else SUCCESS
                unread_message_packet = chat_pb2.GetReply(status=status, errormessage=NO_ERROR)
                for unread in unread_messages:
                    single_message = chat_pb2.UnreadMessage(sender=unread[1], message=unread[2], receiver=request.user)
                    unread_message_packet.message.append(single_message)
                cursor.execute("DELETE FROM messages WHERE recipient = ?", (request.user, ))
                con.commit()
                return unread_message_packet

def set_all_offline():
    with lock:
        with sqlite3.connect(DATABASE_PATH) as con:
            cursor = con.cursor()
            cursor.execute("UPDATE users SET online = FALSE")
            con.commit()

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    try:
        server.wait_for_termination()
        set_all_offline()
    except KeyboardInterrupt:
        set_all_offline()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
