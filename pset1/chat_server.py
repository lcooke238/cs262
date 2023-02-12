#imports
import socket
import pandas as pd
import warnings
import threading
import select

#constants
# server_port = '127.0.0.1'
# server_host = 8080
socket_list = []
online_clients = {}
Head_Len = 10
wp_version = 0
log_name = 'server_log.txt'
data = 'data.csv'


#Log(logfilename: String, msg: String): 
    #records msg in log text file with name logfilename
def Log(msg, logfilename=log_name):
    with open(logfilename, 'a') as log:
        log.write(msg + '\n')
        log.flush()


#Rec_Exception(eType: warning or error Class, eMsg: String, logfilename : string): 
    #for given exception type eType, logs a warning with message eMsg
    #in text file log with name logfilename. If eType is not Warning or ValueError,
    #logs faulty error type along with error message eMsg
def Rec_Exception(eType, eMsg, logfilename=log_name):
    #handle warnings
    if eType == Warning:
        warnings.simplefilter("ignore", UserWarning)
        #print warning to server
        warnings.warn(eMsg)
        #log warning
        Log(eMsg, logfilename)
    #handle value errors without terminating anything
    elif eType == ValueError:
        #print error
        msg = "ValueError: " + eMsg
        #print error to server
        warnings.warn(msg)
        #log error
        Log(msg, logfilename)
    #faulty exception passed in, log bad exception type passing with message passed in
    else:
        Log("LogError: faulty exception type passed to Rec_Exception, message passed was: " + eMsg, logfilename)


#Start_Server(sHost: String, sPort: int, logfilename: String, datasetname: String, emptyWarningFlag: Boolean): 
    #create server socket and start listening at host sHost and port sPort
    #access and verify format of database csv file with name datasetname that should contain existing users and stored messages
    #throws warning for an empty database if the warning flag emptyWarningFlag is True
    #logs progress in text log file called logfilename
def Start_Server(sHost, sPort, logfilename=log_name, datasetname=data, emptyWarningFlag=False):
    #setup server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((sHost, sPort))
    #try to access database with users and stored messages
    try: 
        data_df = pd.read_csv(datasetname)
        if data_df.empty and emptyWarningFlag == True:
            #if reachable and empty, throw warning
            Rec_Exception(Warning, 'EmptyDatasetWarning: Input message and client dataset is empty. Did you select the correct file?',logfilename)
        #if existing dataset doesn't have required column, do not use
        elif "ExistingUsers" not in list(data_df.columns):
            raise Exception("Dataset format invalid. Creating new dataset")
    #access failed, record exception and create new dataset to use
    except:
        Rec_Exception(Warning, 'InvalidDatasetWarning: input dataset invalid, creating a new dataset for server to use',logfilename)
        #create new dataset
        new_df = pd.DataFrame({"ExistingUsers": []})
        new_df.to_csv(datasetname, index=False)
    #turn on server and start listening
    server_socket.listen()
    #add server socket to list of sockets for selection
    socket_list = [server_socket]
    #confirmation message server is running
    Log("server is listening for connections..." + str(sHost)+":"+str(sPort), logfilename)


##IN PROGRESS AND UNTESTED BELOW HERE##
#TODO: Wire_to_Function(cSocket,logfilename): 
    # parse and process input data from a given client's socket cSocket and pass to correct local server operation.
    # If loginFlag is True, then only the Login operation will be expected and the rest will cause failure
    #TODO: fix subfunction calls with full arglists
def Wire_to_Function(cSocket, sList=socket_list, onlineClients=online_clients, loginFlag=False, database=data, logfilename=log_name):
    try:
        #Get first 4 bytes for wire protocol version number
        protocol_version = cSocket.recv(4)
        #if we recieve nothing, socket has been shut down/closed on the other end, so we end the call.
        if not len(protocol_version):
            return False
        #check for the expected protocol version number
        protocol_version_decoded = int(protocol_version.decode('utf-8').strip())
        if protocol_version_decoded != wp_version: 
            #get the wrong version, log the error and close the connection
            Rec_Exception(ValueError, "Wire Protocol version does not match. Server expected version " + str(wp_version) + ", got " + str(protocol_version_decoded),logfilename)
            return False
        #otherwise, version is good and we can recieve the operation code
        op_code = cSocket.recv(1)
        op_code_decoded = int(op_code.decode('utf-8').strip())
        #check for invalid op code and communicate faulty operation if found
        #TODO pick num of ops, rn 10
        if op_code_decoded > 4:
            Rec_Exception(ValueError, "Operation Code Faulty. Please ensure that your wire protocol is converting your request properly.",logfilename)
            #send op code exception back to client
            Send_Error(cSocket, "Operation Code Faulty. Please ensure that your wire protocol is converting your request properly.", logfilename)
        elif (op_code_decoded != 3 and loginFlag) or (op_code_decoded == 3 and not loginFlag):
            Rec_Exception(ValueError, "Operation Code Faulty. Login expected only as first communication.",logfilename)
            #send op code exception back to client
            Send_Error(cSocket, "Operation Code Faulty. Login expected only as first communication.", logfilename)
        #grab rest of input length and input from socket with default size in wire protocol
        in_len_decoded = int(cSocket.recv(4).decode('utf-8').strip())
        #for the proper operation code, pass rest of input to the respective function
        match op_code_decoded:
            #0: send message to another user
            case 0:
                Log("sending message from " + onlineClients[cSocket], logfilename)
                Send_Message(cSocket, in_len_decoded, onlineClients, database, logfilename)
                Log("finished sending message from " + onlineClients[cSocket], logfilename)
            #1: logout
            case 1:
                remaining_input = cSocket.recv(in_len_decoded)
                Log("logging out from " + onlineClients[cSocket], logfilename)
                Logout(cSocket, remaining_input, onlineClients, logfilename)
                Log("finished logging out from " + str(cSocket), logfilename)
            #2: Delete account
            case 2:
                remaining_input = cSocket.recv(in_len_decoded)
                Log("deleting account from " + onlineClients[cSocket], logfilename)
                Delete_Acct(cSocket, remaining_input,onlineClients, database, logfilename)
                Log("finished deleting account from " + str(cSocket), logfilename)
            #3: login
            case 3:
                remaining_input = cSocket.recv(in_len_decoded)
                Log("attempting logging in from " + str(cSocket), logfilename)
                Login(cSocket, remaining_input, sList, onlineClients, database, logfilename)
                Log("finished logging in for " + onlineClients[cSocket], logfilename)
            #4: error
            case 4:
                remaining_input = cSocket.recv(in_len_decoded).decode('utf-8').strip()
                Log("recieved error from client" + onlineClients[cSocket], logfilename)
                Rec_Exception(ValueError, remaining_input, logfilename)
    #otherwise socket is broken in some way, nothing left to do
    except:
        return False


#Socket_Select(sSocket, sList): creates list of sockets with requests or errors on them given list of active sockets (sList)
    #handles new connections that come over the sSocket
    #returns False when the process should be repeated
    #all needs to be encased in an infinite loop for use
def Socket_Select(sSocket, sList, onlineClients, database=data, logfilename=log_name):
    #produces list of sockets:
        #that we have recieved data on (rsockets)
        #sockets ready for data to be sent (wSockets)
        #sockets with errors (eSockets)
    rSockets, _, eSockets = select.select(sList, [], sList)
    #go through sockets with information in them
    for rSocket in rSockets:
        #if server socket has content, we have a new connection
        if rSocket == sSocket:
            #accept connection
            cSocket, cAddr = sSocket.accept()
            Log("accepted connection from " + str(cAddr), logfilename)
            #should come with a login request, pass to function converter for handling
            b = Wire_to_Function(cSocket, sList, onlineClients, True, database, logfilename)
            #u_name false means communication failed in some way, stop and repeat process
            if not b:
                return False
        #otherwise existing socket is sending a non-connection operation
        else:
            #decode and do whatever operation sent via rSocket
            Log("recieved operation from socket " + str(rSocket), logfilename)
            b = Wire_to_Function(rSocket, sList, onlineClients, False, database, logfilename)
            #if false, socket bad in some way, connection should be removed
            if not b:
                #log and remove connection from faulty rSocket, repeat process
                Log("no data from socket. connection to socket " + str(rSocket) + "closed.", logfilename)
                sList.remove(rSocket)
                del online_clients[rSocket]
                return False
    
    #handle sockets with errors
    for eSocket in eSockets:
        #kill connection
        Rec_Exception(ValueError, "Socket" + str(eSocket) + "logged as faulty in some way by select.", logfilename)
        sList.remove(eSocket)
        del online_clients[eSocket]


#Login(cSocket, input, sList, onlineClients, dataset, logfilename):
    #appropriately decodes input username and adds to active sockets and onlineClient list
    #if fails, return false
def Login(cSocket, input, sList, onlineClients, dataset=data, logfilename=log_name):
    try:
        #decode input username, input already correct length
        username = input.decode('utf-8').strip()
        #enforce username length cap
        if len(username) > 256:
            username = username[:255]
        #if username already online, fail
        if username in onlineClients or username == "server":
            return False
        #if username doesn't already exist offline, add to list
        data_df = pd.read_csv(dataset)
        if username not in list(data_df["ExistingUsers"]):
            data_df["ExistingUsers"].append(username)
        #succeeded!, add to list of active sockets and dict online clients with the username
        sList.append(cSocket)
        onlineClients[cSocket] = username
        #if username offline with stored messages, bring back and send those messages
        if username in list(data_df.columns):
            msgs = list(dataset[username])
            recip_socket = {i for i in onlineClients if onlineClients[i]==username}
            for msg in msgs:
                recip_socket.send(msg)
            #delete that column from the dataset
            data_df.drop(username)
            Log("sent stored messages to " + username, logfilename)
        data_df.to_csv(dataset, index=False)
    except:
        Rec_Exception(ValueError, "Username could not be parsed from socket " + str(cSocket) + ". login will now fail.", logfilename)
        return False


#def Msg_to_Wire(recip, msg, sender, logfilename):
    #given the sender username, recipient username, and message
    #construct and output encoded bit array as return
def Msg_to_Wire(recip, msg, sender, logfilename=log_name):
    #create byte array
    wire = []
    #first add protocol version number encoded to 4 bits
    wire.append(str(wp_version).encode('utf-8'))
    #add padding to be 4 bytes long
    while len(wire) < 32:
        wire.append(0)
    #add opcode, in this case 0 (already a single byte)
    wire.append(str(0).encode('utf-8'))
    #add length of rest of input: 4+1+len(recip)+len(msg)
    l_recip = len(recip)
    l_msg = len(msg)
    l = 4+1+l_recip+l_msg
    wire.append(str(l).encode('utf-8'))
    #add padding to be 4 bytes
    while len(wire) < 32:
        wire.append(0)
    #add byte for length of recipient username (already a single byte)
    wire.append(str(l_recip).encode('utf-8'))
    #add recipient username
    wire.append(recip.encode('utf-8'))
    #add message
    wire.append(msg.encode('utf-8'))
    #log wire having been built and return the completed wire
    Log("Wire for message reciept built to be sent by " + sender, logfilename)
    return wire


#def Send_Message(cSocket, inlen, onlineClients, logfilename):
    #returns false on failure
def Send_Message(cSocket, inlen, onlineClients, database=data, logfilename=log_name):
    #decode recipient username and message according to wire protocol
    len_recip = int(cSocket.recv(1).decode('utf-8').strip())
    recip = str(cSocket.recv(len_recip).decode('utf-8').strip())
    msg = str(cSocket.recv(inlen-1-len_recip).decode('utf-8').strip())
    #get sender's username from live clients
    sender = onlineClients[cSocket]
    Log("recipient, message, and sender successfully retrieved from socket " + onlineClients[cSocket] ,logfilename)
    #if recipient does not exist, fail
    data_df = pd.read_csv(database)
    if recip not in list(data_df["ExistingUsers"]):
        return False
    #find recipient and send to them
    recip_socket = {i for i in onlineClients if onlineClients[i]==recip}
    #get converted message
    wire = Msg_to_Wire(recip,msg,sender,logfilename)
    #if recip online, send message
    if recip in onlineClients:
        recip_socket.send(wire)
    #otherwise offline, store in database for future send
    else:
        #if col for this user exists, add encoded message there
        if recip in list(data_df.columns):
            data_df[recip].append(wire)
        #if it doesn't exist, insert a column with that addr
        else:
            data_df.insert(2, recip, [wire], True)
        #save dataframe to csv
        data_df.to_csv(database, index=False)


#send error function
#def Send_Error(cSocket, eType, eMsg, logfilename):
    #encodes error message and sends to cSocket
def Send_Error(cSocket, eMsg, logfilename=log_name):
    #encode error with wire protocol function
    #create byte array
    wire = []
    #first add protocol version number encoded to 4 bits
    wire.append(str(wp_version).encode('utf-8'))
    #add padding to be 4 bytes long
    while len(wire) < 32:
        wire.append(0)
    #add opcode, in this case 0 (already a single byte)
    wire.append(str(4).encode('utf-8'))
    #add length of message
    wire.append(str(len(eMsg)).encode('utf-8'))
    #add padding to be 4 bytes long
    while len(wire) < 32:
        wire.append(0)
    #add message
    wire.append(eMsg.encode('utf-8'))
    #send encoded error
    Log("built error wire to send to client" + str(cSocket), logfilename)
    cSocket.send(wire)


#delete account function
def Delete_Acct(cSocket, input, onlineClients=online_clients, database=data, logfilename=log_name):
    #decode confirmatory username
    confirm = input.decode('utf-8').strip()
    #ensure confirmatory username and cSocket username match
    if confirm == onlineClients[cSocket]:
        Log("deletion confirmed. Beginning account deletion process for " + confirm, logfilename)
        #send confirmation message
        cSocket.send(Msg_to_Wire(confirm, "account deleted. Client shutting down.","server",logfilename))
        #remove from online clients database, active sockets and existing clients
        onlineClients.remove(cSocket)
        data_df = pd.read_csv(database)
        data_df["ExistingUsers"].drop(confirm)
    #otherwise, deletion won't occur. 
    else:
        Rec_Exception(ValueError, "deletion failed. Ensure that you send your username along with the deletion request.",logfilename)
        Send_Error(cSocket, "deletion failed. Ensure that you send your username along with the deletion request.",logfilename)


#logout function
def Logout(cSocket, input, onlineClients=online_clients, logfilename=log_name):
    #decode confirmatory username
    confirm = input.decode('utf-8').strip()
    #ensure confirmatory username and cSocket username match
    if confirm == onlineClients[cSocket]:
        Log("logout confirmed. Beginning account logout process for " + confirm, logfilename)
        #send confirmation message
        cSocket.send(Msg_to_Wire(confirm, "logged out. Client shutting down.","server",logfilename))
        #remove from online clients database and active sockets
        onlineClients.remove(cSocket)
    #otherwise, logout won't occur. 
    else:
        Rec_Exception(ValueError, "logout failed. Ensure that you send your username along with the logout request.",logfilename)
        Send_Error(cSocket, "logout failed. Ensure that you send your username along with the logout request.",logfilename)

    
    


#TODO: server execution