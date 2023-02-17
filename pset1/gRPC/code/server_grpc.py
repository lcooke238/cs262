from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc

from collections import defaultdict

SUCCESS = 0
FAILURE = 1

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
        if request.name in logged_in_users:
            return chat_pb2.LoginReply(errormessage="User already logged in on different machine", status=FAILURE)
        logged_in_users.append(request.name)
        if request.name in users:
            login_reply = chat_pb2.LoginReply(status = SUCCESS, errormessage=NO_ERROR, user=request.name)
            for unread in unread_messages.get(request.name, []):
                login_reply.message.append(unread)
            return login_reply
        else:
            users.append(request.name)
            return chat_pb2.LoginReply(status=SUCCESS, errormessage=NO_ERROR, user=request.name)
        
    def Logout(self, request, context):
        if request.name in logged_in_users:
            logged_in_users.remove(request.name)
            return chat_pb2.LogoutReply(status=SUCCESS, errormessage=NO_ERROR, user=request.name)
        return chat_pb2.LogoutReply(status=FAILURE, errormessage="User not currently logged in", user=request.name)
    
    def Delete(self, request, context):
        logged_in_users.remove(request.name)
        users.remove(request.name)
        return chat_pb2.DeleteReply(status=SUCCESS, errormessage=NO_ERROR, user=request.name)

    def ListUsers(self, request, context):
        wildcard = request.args.strip()
        # Basic wildcard, is name equal to a name in the list, or is it *
        if wildcard == "*":
            user_list = chat_pb2.ListReply(status=SUCCESS, wildcard=wildcard, errormessage="")
            for user in users:
                user_list.user.append(user)
            return user_list
        return chat_pb2.ListReply(status=FAILURE, wildcard=wildcard, errormessage="NOT_IMPLEMENTED", user="[NOT_IMPLEMENTED]")

    def Send(self, request, context):
        print("Not sending well")
        if request.target not in users:
            return chat_pb2.SendReply(status=FAILURE, errormessage="User does not exist :(", user=request.name, message="[]", target=request.target)
        unread_messages[request.target].append(request.message)
        print(unread_messages)
        if request.target not in logged_in_users:
            return chat_pb2.SendReply(status=SUCCESS, errormessage="User offline, message will be received upon login", user=request.name, message="[]", target=request.target)
        # Should I have a ServerHandler for each client that accepts messages here? How to handle this case? Streams?
        return chat_pb2.SendReply(status=SUCCESS, errormessage=NO_ERROR, user=request.name, message="[]", target=request.target) 

    def GetMessages(self, request, context):
        if request.user not in users:
            return chat_pb2.GetReply(status=FAILURE, errormessage="User does not exist :(")
        unread_message_packet = chat_pb2.GetReply(status=SUCCESS, errormessage=NO_ERROR)
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
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
