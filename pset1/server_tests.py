#imports
import chat_server
import pandas as pd
import os

#log function tests
def test_log(logfilename):
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 1: Logging initial message works
    chat_server.Log(logfilename, "hi")
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
        chat_server.Log(logfilename, msg)
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


#server_startup function tests
def test_server_startup(host, port, logfilename):
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 1: works when used correctly with expected dataset
    chat_server.Start_Server(host, port, logfilename, 'test_data.csv')
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "server is listening for connections...":
            print("Startup Test 1 Passed")
        else:
            raise Exception("Startup Test 1 Failed. Log should read \"server is listening for connections...\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 2: single empty dataset warning logged when passed empty dataset
    chat_server.Start_Server(host, port, logfilename, 'test_data_empty.csv')
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "EmptyDatasetWarning: Input message and client dataset is empty. Did you select the correct file?":
            pass
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"EmptyDatasetWarning: Input message and client dataset is empty. Did you select the correct file?\", but instead reads \"" + content[0].strip()+"\"")
        if content[1].strip() == "server is listening for connections...":
            print("Startup Test 2 Passed")
        else:
            raise Exception("Startup Test 2 Failed. Log should read \"server is listening for connections...\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log
    open(logfilename, 'w').close()

    #Test 3: exception logged when passed invalid dataset
    chat_server.Start_Server(host, port, logfilename, 'invalid.csv')
    #open log to read it
    with open(logfilename, 'r') as log:
        content = log.readlines()
        if content[0].strip() == "InvalidDatasetWarning: input dataset invalid, creating a new dataset for server to use":
            pass
        else:
            raise Exception("Startup Test 3 Failed. Log should read \"InvalidDatasetWarning: input dataset invalid, creating a new dataset for server to use\", but instead reads \"" + content[0].strip()+"\"")
        #ensure content of dataset is correct
        test_df = pd.read_csv('invalid.csv')
        compare_df = pd.DataFrame({'Online':[], 'Offline':[]})
        if test_df.to_string() == compare_df.to_string():
            pass
        else:
            raise Exception("Startup Test 3 Failed. New dataset should contain " + compare_df.to_string() + ", but instead contains " + test_df.to_string())
        if content[1].strip() == "server is listening for connections...":
            print("Startup Test 3 Passed")
        else:
            raise Exception("Startup Test 3 Failed. Log should read \"server is listening for connections...\", but instead reads \"" + content[0].strip()+"\"")
    #clear content of test log and remove invalid dataset
    os.remove('invalid.csv')
    open(logfilename, 'w').close()

#run tests
test_log('test_log.txt')
test_rec_exception('test_log.txt')
test_server_startup('127.0.0.1', 8080, 'test_log.txt')
print("full server test suite passed")
