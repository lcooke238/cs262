#imports
import server_custom as chat_server
import client_custom as chat_client
import time



# TEST_CUSTOM
#   test suite for client_custom.py and server_custom.py;
#   run by running test_server.py in a separate tab,
#   and running 'pytest' in the directory that contains this file.

#constants
server_host = '127.0.0.1'
server_port = 8080
client_host = "127.0.0.1"
client_port = 1234
socket_list = []
online_clients = {}
Head_Len = 4
wp_version = 0
log_name_s = '../logs/testing/test_server_log.txt'
log_name_c = '../logs/testing/test_client_log.txt'
log_name_t = '../logs/testing/test_log.txt'
empty_data = '../data/testing/test_data_empty.csv'
data = '../data/testing/test_data.csv'
users = '../data/testing/test_users.csv'

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
    chat_server.Start_Server(host, port, logfilename, data, users)
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
    chat_server.Start_Server(host, port, logfilename, empty_data, users, 1)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "EmptyDatasetWarning: Input message dataset is empty. Did you select the correct file?":
            pass
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"EmptyDatasetWarning: Input message dataset is empty. Did you select the correct file?\", but instead reads \"" + content[0].strip()+"\"")
        if content[1].strip() == "server is listening for connections..." + str(host)+":"+str(port):
            print("Startup Test 2 Passed")
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"server is listening for connections..." + str(host)+":"+str(port)+ "\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()
    
    #Test 3: no exception logged for empty dataset with flag off
    chat_server.Start_Server(host, port, logfilename, empty_data, users, 0)
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "server is listening for connections..."+ str(host)+":"+str(port):
            print("Startup Test 3 Passed")
        else:
            raise Exception("Startup Test 3 Failed. Log should read \"server is listening for connections..."+ str(host)+":"+str(port)+"\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()

#help in chat client function tests, assumes server is running in a separate terminal
def test_help(logfilename):
    #start client
     #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run help call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\help")
    #ensure help was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[3].strip() == "Welcome to the chat service, Lauren! Here is a list of commands available to you and their syntax:"
    print("help test passed")


#list in chat client function tests, assumes server is running in a separate terminal
def test_list(logfilename):
    #start client
     #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run help call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\list *")
    #ensure list request was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[4].strip() == "listUsr message sent"
    print("list test 1 passed")
    #add delay for socket to send properly
    time.sleep(1)
    chat_client.IO_Manager(cSocket, username, logfilename, True, " ")
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[5].strip() == "users from query:"
        assert content[6].strip() == "Lauren,"
    print("list test 2 passed")


#test sending to a client, assumes server is running in a separate channel
def test_send(logfilename):
    #start client
    #clear client log
    open(logfilename, 'w').close()
    #clear server log
    open(log_name_s, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run send call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\send Hi!\\,Lauren")
    #ensure send request was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[4].strip() == "message sent to Lauren"
    print("send test 1 passed")
    #add delay for socket to send properly
    time.sleep(1)
    chat_client.IO_Manager(cSocket, username, logfilename, True, " ")
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[6].strip() == "Lauren > Hi!"
    print("send test 2 passed")



#logout in chat client function tests, assumes server is running in a separate terminal
def test_logout(logfilename):
    #start client
    #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run logout call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\logout", "yes")
    #ensure logout was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[4].strip() == "logout message sent"
    print("logout test 1 passed")

    #start client
    #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run logout call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\logout", "no")
    #ensure logout was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        try: 
            content[4].strip()
            assert False
        except:
            print("logout test 2 passed")


#delete in chat client function tests, assumes server is running in a separate terminal
def test_delete(logfilename):
    #start client
    #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run logout call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\delete", "yes")
    #ensure logout was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        assert content[4].strip() == "delete message sent"
    print("delete test 1 passed")

    #start client
    #clear client log
    open(logfilename, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, logfilename, True, "Lauren")
    #run logout call
    chat_client.IO_Manager(cSocket, username, logfilename, True, "\\delete", "no")
    #ensure logout was logged
    with open(logfilename, 'r') as log:
        content = log.readlines()
        try: 
            content[4].strip()
            assert False
        except:
            print("delete test 2 passed")



#run tests
test_log(log_name_t)
test_rec_exception(log_name_t)
test_server_startup('127.0.0.1', 8080, log_name_t)
#clear server log
open(log_name_s, 'w').close()
test_help(log_name_c)
test_list(log_name_c)
test_send(log_name_c)
test_logout(log_name_c)
test_delete(log_name_c)


print("full server test suite passed")
