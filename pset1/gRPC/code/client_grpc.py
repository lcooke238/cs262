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
"""The Python implementation of the GRPC helloworld.ClientHandler client."""

from __future__ import print_function

import logging

import grpc
import chat_pb2
import chat_pb2_grpc

SUCCESS = 0
FAILURE = 1

user_token = ""

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        ClientHandler(channel)


def attempt_login(stub):
    global user_token
    user = input("Please enter a username: ")
    # Attempt login on server
    response = stub.Login(chat_pb2.LoginRequest(name=user))
    # If failure, print failure and return, they can attempt again
    if response.status == FAILURE:
        print(f"Login error: {response.errormessage}")
        return
    # If success, set user token
    user_token = response.user
    # Print success message
    print(f"Succesfully logged in as user: {user_token}. Unread messages:")
    # Print all unread messages
    for message in response.message:
        print(message)

def attempt_list(stub, args):
    # Attempt to retrieve user list from server
    response = stub.ListUsers(chat_pb2.ListRequest(args=args))
    # If failed, print failure and return
    if response.status == FAILURE:
        print(f"List users failed, error: {response.errormessage}")
        return
    # If success, print users that match the wildcard provided
    print(f"Users matching wildcard {response.wildcard}:")
    for user in response.user:
        print(user)
        
def attempt_logout(stub):
    global user_token
    response = stub.Logout(chat_pb2.LogoutRequest(name=user_token))
    if response.status == FAILURE:
        print(f"Logout error: {response.errormessage}")
        return
    user_token = ""
    return

def process_command(stub, command):
    if len(command) < 5:
        print("Invalid command, try \help for list of commands")
        return
    if command[0:5] == "\\list":
        attempt_list(stub, command[5:])
    if command[0:5] == "\\send":
        pass
    if command[0:7] == "\\logout":
        attempt_logout(stub)

def ClientHandler(channel):
    global user_token
    stub = chat_pb2_grpc.ClientHandlerStub(channel)
    while True:
        if user_token:
            command = input(f"{user_token} >")
            process_command(stub, command)
        else:
            attempt_login(stub)
        


if __name__ == '__main__':
    logging.basicConfig()
    run()
