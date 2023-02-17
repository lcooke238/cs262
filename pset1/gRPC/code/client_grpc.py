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

def attempt_delete(stub):
    global user_token
    stub.Delete(chat_pb2.DeleteRequest(name=user_token))
    # No way of this actually failing is there really? Unless server goes offline?
    # Maybe should still check response
    user_token = ""
    return

def attempt_send(stub, args):
    global user_token
    arg_list = args.split("->").strip()
    if len(arg_list) != 2:
        print("Invalid message send syntax. Correct syntax: \send {message} -> {user}")
        return
    message = arg_list[0]
    target = arg_list[1]
    response = stub.Send(chat_pb2.SendRequest(name=user_token, message=message, target=target))

def handle_invalid_command(command):
    print(f"Invalid command: {command}, please try \help for list of commands")

def display_command_help():
    print(" -- Valid commands --")
    print(" \help -> Gives this list of commands")
    print(" \logout -> logs out of your account")
    print(" \delete -> deletes your account")
    print(" \send -> currently not implemented")
    print(" \list wildcard -> lists all users that match the wildcard provided")

def process_command(stub, command):
    if len(command) < 5:
        handle_invalid_command(command)
        return
    if command[0:5] == "\\help":
        display_command_help()
    if command[0:5] == "\\list":
        attempt_list(stub, command[5:])
    if command[0:5] == "\\send":
        attempt_send(stub, command[5:])
    if len(command < 7):
        handle_invalid_command(command)
        return
    if command[0:7] == "\\logout":
        attempt_logout(stub)
    if command[0:7] == "\\delete":
        attempt_delete(stub)

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
