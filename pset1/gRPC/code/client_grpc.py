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
    response = stub.Login(chat_pb2.LoginRequest(name=user))
    print(response.message, user)
    if response.status == FAILURE:
        print(f"Login error: {response.message}")
    else:
        user_token = response.message
        print(f"Succesfully logged in as user: {user_token}")

def attempt_list(stub, args):
    response = stub.ListUsers(chat_pb2.ListRequest(args=args))
    if response.status == SUCCESS:
        print(f"Users matching wildcard {response.wildcard}:")
        for user in response.user:
            print(user)
    else:
        print(f"List users failed, error: {response.message}")



def ClientHandler(channel):
    global user_token
    stub = chat_pb2_grpc.ClientHandlerStub(channel)
    while True:
        if user_token:
            command = input(f"{user_token} >")
            if len(command) < 6:
                raise Exception
            match command[0:5]:
                case "\\list":
                    attempt_list(stub, command[5:])
        else:
            attempt_login(stub)
        


if __name__ == '__main__':
    logging.basicConfig()
    run()
