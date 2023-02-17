# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.ClientHandler server."""

from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc

SUCCESS = 0
FAILURE = 1

NO_ERROR = ""

# Playing with state
storage = {}
users = ["andrew", "ben"]
logged_in_users = ["ben"]
unread_messages = {"andrew": ["ben > Hey Andrew", "andrew > Note to self: turn this into db"]}
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
