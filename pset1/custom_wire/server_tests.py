#imports
import server_custom as chat_server
import client_custom as chat_client
import pandas as pd
import threading
import sys
from pytest import monkeypatch
import io

#constants
server_host = '127.0.0.1'
server_port = 1234
client_host = "127.0.0.1"
client_port = 1234
socket_list = []
online_clients = {}
Head_Len = 4
wp_version = 0
log_name_s = 'test_server_log.txt'
log_name_c = 'test_client_log.txt'
data = 'test_data.csv'
users = 'test_users.csv'

#log function tests
def test_log(logfilename):
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 1: Logging initial message works
    chat_server.Log("hi", logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.read().strip()
        #if test log content contains exactly the message of interest
        if content == "hi":
            #test passed, clear log
            print("Log Test 1 Passed")
        else:
            raise Exception("Log Test 1 Failed. the log should read hi, but instead read " + content)
    #clear file content
    open(logfilename, 'w').close()

    #Test 2: logging multiple messages works
    messages = ["hi", "hello", "bye"]
    for msg in messages:
        chat_server.Log(msg, logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        for i in range(len(messages)):
            if content[i].strip() != messages[i]:
                raise Exception("Log Test 2 Failed. Line " + str(i) + " should read " + messages[i]+", but instead reads " + content[i].strip())
        print("Log Test 2 Passed")
    #clear file content
    open(logfilename, 'w').close()            


#rec_exception function tests
def test_rec_exception(logfilename):
    #clear content of test log
    open(logfilename, 'w').close()
    
    #Test 1: Log a warning
    chat_server.Rec_Exception(Warning, "WarningName: Sample warning message", logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.read().strip()
        #if test log content contains exactly the message of interest
        if content == "WarningName: Sample warning message":
            #test passed, clear log
            print("Exception Test 1 Passed")
        else:
            raise Exception("Exception Test 1 Failed. the log should read WarningName: Sample warning message, but instead read " + content)
    #clear file content
    open(logfilename, 'w').close()

    #Test 2: Log multiple warnings
    warnings = ["WarningName: A", "WarningName: B", "WarningName: C"]
    for warn in warnings:
        chat_server.Rec_Exception(Warning, warn, logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        for i in range(len(warnings)):
            if content[i].strip() != warnings[i]:
                raise Exception("Exception Test 2 Failed. Line " + str(i) + " should read " + warnings[i]+", but instead reads " + content[i].strip())
        print("Exception Test 2 Passed")
    #clear file content
    open(logfilename, 'w').close() 

    #Test 3: Log a value error
    chat_server.Rec_Exception(ValueError, "Sample valueError message", logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.read().strip()
        #if test log content contains exactly the message of interest
        if content == "ValueError: Sample valueError message":
            #test passed, clear log
            print("Exception Test 3 Passed")
        else:
            raise Exception("Exception Test 3 Failed. the log should read\"ValueError: Sample valueError message\", but instead read " + content)
    #clear file content
    open(logfilename, 'w').close()

    #Test 4: Log a faulty warning type followed by a value error and a warning
    chat_server.Rec_Exception(FloatingPointError, "Sample FloatingPointError message", logfilename)
    chat_server.Rec_Exception(ValueError, "Sample valueError message", logfilename)
    chat_server.Rec_Exception(Warning, "Warning: Sample Warning Message", logfilename)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        #if test log content contains exactly the message of interest
        if content[0].strip() == "LogError: faulty exception type passed to Rec_Exception, message passed was: Sample FloatingPointError message":
            pass
        else:
            raise Exception("Exception Test 4 Failed. the log should read \"LogError: faulty exception type passed to Rec_Exception, message passed was: Sample FloatingPointError message\", instead read \""+content[0].strip()+"\"")
        if content[1].strip() == "ValueError: Sample valueError message":
            pass
        else:
            raise Exception("Exception Test 4 Failed. the log should read \"ValueError: Sample valueError message\", instead read \""+content[1].strip()+"\"")
        if content[2].strip() == "Warning: Sample Warning Message":
            print("Exception Test 4 Passed")
        else:
            raise Exception("Exception Test 4 Failed. the log should read \"Warning: Sample Warning message\", instead read \""+content[2].strip()+"\"")
    #clear file content
    open(logfilename, 'w').close()


#server_startup function tests
def test_server_startup(host, port, logfilename):
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 1: works when used correctly with expected dataset
    chat_server.Start_Server(host, port, logfilename, 'test_data.csv', 'test_users.csv')
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "server is listening for connections..." + str(host)+":"+str(port):
            print("Startup Test 1 Passed")
        else:
            raise Exception("Startup Test 1 Failed. Log should read \"server is listening for connections..." + str(host
            )+":"+str(port) + "\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 2: single empty dataset warning logged when passed empty dataset with flag on
    chat_server.Start_Server(host, port, logfilename, 'test_data_empty.csv','test_users.csv', 1)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "EmptyDatasetWarning: Input message dataset is empty. Did you select the correct file?":
            pass
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"EmptyDatasetWarning: Input message dataset is empty. Did you select the correct file?\", but instead reads \"" + content[0].strip()+"\"")
        if content[1].strip() == "EmptyDatasetWarning: Input client dataset is empty. Did you select the correct file?":
            pass
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"EmptyDatasetWarning: Input client dataset is empty. Did you select the correct file?\", but instead reads \"" + content[0].strip()+"\"")
        if content[2].strip() == "server is listening for connections..." + str(host)+":"+str(port):
            print("Startup Test 2 Passed")
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"server is listening for connections..." + str(host)+":"+str(port)+ "\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()
    
    #Test 3: no exception logged for empty dataset with flag off
    chat_server.Start_Server(host, port, logfilename, 'test_data_empty.csv','test_users.csv', 0)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "server is listening for connections..."+ str(host)+":"+str(port):
            print("Startup Test 3 Passed")
        else:
            raise Exception("Startup Test 3 Failed. Log should read \"server is listening for connections..."+ str(host)+":"+str(port)+"\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()

   

#TODO Wire_to_Function tests
def test_WtoF(cSocket, logfilename):
    pass


#TODO Socket_Select tests
def test_sSelect(sSocket, sList, onlineClients, database, logfilename):
    pass


#TODO Login tests
def test_login():
    pass


#TODO Msg_to_Wire tests
def test_MtoW():
    pass


#TODO Send_Message tests
def test_send_msg():
    pass


#TODO Delete_Acct tests
def test_delete():
    pass


#TODO Logout tests
def test_logout():
    pass


#TODO List_Accounts tests
def test_list_acct():
    pass


#run_server, uses constants from above to turn on a server
def run_server(server_socket):
    #infinitely select through sockets
    while True:
        chat_server.Socket_Select(server_socket, socket_list, online_clients, data, users, log_name_s)


#runs client tests that require server connection
def remaining_client_tests():
    #connect to created server from first thread
    #clear client log
    open(log_name_c, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, log_name_c)
    monkeypatch.setattr('sys.stdin', io.StringIO('Lauren'))
    sys.exit()


#run tests
test_log('test_log.txt')
test_rec_exception('test_log.txt')
test_server_startup('127.0.0.1', 8080, 'test_log.txt')
#first, create a socket pointing back to yourself in a different thread
#clear server log
open(log_name_s, 'w').close()
#startup server
server_socket = chat_server.Start_Server(server_host, server_port, log_name_s, data, users, False)
#add server socket to list of sockets for selection
socket_list = [server_socket]
t1 = threading.Thread(target=remaining_client_tests())
t1.start()
run_server(server_socket)
#multithread to run the other tests with a client
#test_WtoF()
#test_sSelect()
#test_login()
#test_MtoW()
#test_send_msg()
#test_delete()
#test_logout()
#test_list_acct()
print("full server test suite passed")
