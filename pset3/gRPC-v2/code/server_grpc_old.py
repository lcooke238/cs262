from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc
import threading
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
    # Logs a user in
    def Login(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                # Check whether already logged in
                logged_in = cursor.execute("SELECT online FROM users WHERE user=?", (request.user, )).fetchall()
                # User doesn't exist (returned empty list)
                if not logged_in:
                    cursor.execute("INSERT INTO users (user, online) VALUES (?, ?)", (request.user, True))
                    con.commit()
                    return chat_pb2.LoginReply(status = SUCCESS, errormessage=NO_ERROR, user=request.user)
                # Currently logged in
                if logged_in[0][0]:
                    return chat_pb2.LoginReply(status=FAILURE, errormessage="User already logged in on different machine", user=request.user)
                # User exists but not currently logged in
                else:
                    cursor.execute("UPDATE users SET online = ? WHERE user = ?", (True, request.user, ))
                    con.commit()
                    return chat_pb2.LoginReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)
        
    # Logs a user out
    def Logout(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                # They should be logged in to be able to run this, but just checking to avoid errors
                logged_in = cursor.execute("SELECT user FROM users WHERE user = ?", (request.user, )).fetchall()
                if logged_in and logged_in[0]:
                    cursor.execute("UPDATE users SET online = FALSE WHERE user = ?", (request.user, ))
                    con.commit()
                    return chat_pb2.LogoutReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)
                return chat_pb2.LogoutReply(status=FAILURE, errormessage="User not currently logged in", user=request.user)
    
    # Deletes a user from the database
    def Delete(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                # They should be logged in to be able to run this, but just checking to avoid errors
                logged_in = cursor.execute("SELECT online FROM users WHERE user = ?", (request.user, )).fetchall()
                if logged_in:
                    cursor.execute("DELETE FROM users WHERE user = ?", (request.user, ))
                    con.commit()
                return chat_pb2.DeleteReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user)

    # Lists users in the database using SQL wildcard syntax
    def ListUsers(self, request, context):
        wildcard = request.args.strip()
        with sqlite3.connect(DATABASE_PATH) as con:
            cursor = con.cursor()
            # No real way for this to fail so just set as SUCCESS
            user_list = chat_pb2.ListReply(status=SUCCESS, wildcard=wildcard, errormessage="")
            # Pull users according to SQL wildcard
            matched_users = cursor.execute("SELECT user FROM users WHERE user LIKE ?", (wildcard, )).fetchall()
            for user in matched_users:
                user_list.user.append(user[0])
            return user_list

    # Sends a message from one client to another
    def Send(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                # Check whether the name they gave to send to is valid user
                target_check = cursor.execute("SELECT user FROM users WHERE user = ?", (request.user, ))
                if not target_check:
                    return chat_pb2.SendReply(status=FAILURE, errormessage="User does not exist :(", user=request.user, message=request.message, target=request.target)
                # Put message into database
                cursor.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)", (request.user, request.message, request.target, ))
                con.commit()
                return chat_pb2.SendReply(status=SUCCESS, errormessage=NO_ERROR, user=request.user, message=request.message, target=request.target) 

    # Pulls messages from server to client
    def GetMessages(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cursor = con.cursor()
                # Checking for an error, they should be logged in to be running this command
                user_check = cursor.execute("SELECT online FROM users WHERE user = ?", (request.user, )).fetchall()
                if not user_check or not user_check[0][0]:
                    return chat_pb2.GetReply(status=FAILURE, errormessage="User does not exist :(")
                # Pull unread messages. Set return status depending on presence of unread messages
                unread_messages = cursor.execute("SELECT * FROM messages WHERE recipient = ?", (request.user, )).fetchall()
                status = SUCCESS_WITH_DATA if unread_messages else SUCCESS
                # Add all unread messages to a packet
                unread_message_packet = chat_pb2.GetReply(status=status, errormessage=NO_ERROR)
                for unread in unread_messages:
                    single_message = chat_pb2.UnreadMessage(sender=unread[1], message=unread[2], receiver=request.user)
                    unread_message_packet.message.append(single_message)
                # Remove those messages from the unread database. Note that we had the lock, so no new messages
                # could've arrived during this time
                cursor.execute("DELETE FROM messages WHERE recipient = ?", (request.user, ))
                con.commit()
                return unread_message_packet

# Takes the lock and sets all users offline 
def set_all_offline():
    with lock:
        with sqlite3.connect(DATABASE_PATH) as con:
            cursor = con.cursor()
            cursor.execute("UPDATE users SET online = FALSE")
            con.commit()

# Runs the server logic
def serve():
    # Handling any weird crashes to ensure users can still log in
    set_all_offline()
    # Run server
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    # Shutdown nicely
    try:
        server.wait_for_termination()
        set_all_offline()
    except KeyboardInterrupt:
        set_all_offline()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
