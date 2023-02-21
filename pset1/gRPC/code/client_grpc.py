from __future__ import print_function
# from concurrent import futures
import logging

from _thread import *
import threading
import sys

import grpc
import chat_pb2
import chat_pb2_grpc

SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

user_token = ""
server_online = False 
HOST_IP = "localhost"
PORT = "50051"

def run():
    global server_online
    with grpc.insecure_channel(HOST_IP + ":" + PORT) as channel:
        server_online = True
        ClientHandler(channel)

def handle_server_shutdown():
    print("Error: server error")
    sys.exit()

def attempt_login(stub, condition):
    global user_token
    user = input("Please enter a username: ")
    # Attempt login on server
    try:
        response = stub.Login(chat_pb2.LoginRequest(user=user))
    except: 
        handle_server_shutdown()
    # If failure, print failure and return, they can attempt again
    if response.status == FAILURE:
        print(f"Login error: {response.errormessage}")
        return
    # If success, set user token
    user_token = response.user
    # Print success message
    print(f"Succesfully logged in as user: {user_token}. Unread messages:")
    # Notify listener thread to start listening
    with condition:
        condition.notify_all()

def attempt_list(stub, args):
    # Attempt to retrieve user list from server
    try:
        response = stub.ListUsers(chat_pb2.ListRequest(args=args))
    except:
        handle_server_shutdown()
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
    try:
        response = stub.Logout(chat_pb2.LogoutRequest(user=user_token))
    except: 
        handle_server_shutdown()
    if response.status == FAILURE:
        print(f"Logout error: {response.errormessage}")
        return
    user_token = ""
    return

def attempt_delete(stub):
    global user_token
    try:
        stub.Delete(chat_pb2.DeleteRequest(user=user_token))
    except:
        handle_server_shutdown()
    # No way of this actually failing is there really? Unless server goes offline?
    # Maybe should still check response
    user_token = ""
    return

def attempt_send(stub, args):
    global user_token
    arg_list = args.split("->")
    arg_list = [arg.strip() for arg in arg_list]
    if len(arg_list) != 2:
        print("Invalid message send syntax. Correct syntax: \send {message} -> {user}")
        return
    message = arg_list[0]
    target = arg_list[1]
    try:
        response = stub.Send(chat_pb2.SendRequest(user=user_token, message=message, target=target))
    except:
        handle_server_shutdown()

def handle_invalid_command(command):
    print(f"Invalid command: {command}, please try \help for list of commands")

def display_command_help():
    print(" -- Valid commands --")
    print(" \help -> Gives this list of commands")
    print(" \quit -> Exits the program")
    print(" \logout -> logs out of your account")
    print(" \delete -> deletes your account")
    print(" \send message -> {target_user} -> sends message to target_user")
    print(" \list {wildcard} -> lists all users that match the SQL wildcard provided, e.g. \list % lists all users")

def process_command(stub, command):
    if len(command) < 5:
        handle_invalid_command(command)
        return True
    if command[0:5] == "\\help":
        display_command_help()
        return True
    if command[0:5] == "\\list":
        attempt_list(stub, command[5:])
        return True
    if command[0:5] == "\\send":
        attempt_send(stub, command[5:])
        return True
    if command[0:5] == "\\quit":
        attempt_logout(stub)
        return False
    if len(command) < 7:
        handle_invalid_command(command)
        return True
    if command[0:7] == "\\logout":
        attempt_logout(stub)
        return True
    if command[0:7] == "\\delete":
        attempt_delete(stub)
        return True

def ClientHandler(channel):
    global user_token
    stub = chat_pb2_grpc.ClientHandlerStub(channel)
    condition = threading.Condition()
    # Start new Daemon thread listening for messages with condition variable
    # to sync with main thread to have blocking rather than polling
    start_new_thread(listen, (stub, condition, ))
    while True:
        if not server_online:
            handle_server_shutdown()
        try:
            if user_token:
                command = input(f"{user_token} >")
                if not process_command(stub, command):
                    break
            else:
                attempt_login(stub, condition)
        except KeyboardInterrupt:
            attempt_logout(stub)
            print("Logging you out!")
            break
        

def listen(stub, condition):
    global server_online
    while True:
        if user_token:
            try:
                response = stub.GetMessages(chat_pb2.GetRequest(user=user_token))
            except:
                server_online = False
                break
            if response.status == SUCCESS_WITH_DATA:
                for message in response.message:
                    print(f"{message.sender} > {message.message}")
                print(f"{user_token} >", end="")
        else:
            with condition:
                condition.wait()

if __name__ == '__main__':
    logging.basicConfig()
    run()
