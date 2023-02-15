#imports
import socket
import pandas as pd
import warnings
import select

#constants
server_host = '127.0.0.1'
server_port = 1234
socket_list = []
online_clients = {}
Head_Len = 4
wp_version = 0
log_name = 'server_log.txt'
data = 'data.csv'
users = 'users.csv'


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


#Start_Server(sHost: String, sPort: int, logfilename: String, database: String, emptyWarningFlag: Boolean): 
    #create server socket and start listening at host sHost and port sPort
    #access and verify format of database csv file with name database that should contain existing users and stored messages
    #throws warning for an empty database if the warning flag emptyWarningFlag is True
    #logs progress in text log file called logfilename
    #returns server socket on success
def Start_Server(sHost, sPort, logfilename=log_name, database=data, userbase=users, emptyWarningFlag=False):
    #setup server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((sHost, sPort))
    #try to access database with stored messages
    try: 
        data_df = pd.read_csv(database)
        if data_df.empty and emptyWarningFlag == True:
            #if reachable and empty, throw warning
            Rec_Exception(Warning, 'EmptyDatasetWarning: Input message dataset is empty. Did you select the correct file?',logfilename)
        #if existing dataset doesn't have required column, do not use
        elif "ExistingUsers" not in list(data_df.columns):
            raise Exception("Dataset format invalid. Creating new dataset")
    #access failed, record exception and create new dataset to use
    except:
        Rec_Exception(Warning, 'InvalidDatasetWarning: Input message invalid, creating a new dataset for server to use',logfilename)
        #create new dataset
        new_df = pd.DataFrame({"ExistingUsers": []})
        new_df.to_csv(database, index=False)
    #try to access database with users messages
    try: 
        user_df = pd.read_csv(userbase)
        if user_df.empty and emptyWarningFlag == True:
            #if reachable and empty, throw warning
            Rec_Exception(Warning, 'EmptyDatasetWarning: Input client dataset is empty. Did you select the correct file?',logfilename)
        #if existing dataset doesn't have required column, do not use
        elif "ExistingUsers" not in list(user_df.columns):
            raise Exception("Dataset format invalid. Creating new dataset")
    #access failed, record exception and create new dataset to use
    except:
        Rec_Exception(Warning, 'InvalidDatasetWarning: input dataset invalid, creating a new dataset for server to use',logfilename)
        #create new dataset
        user_df = pd.DataFrame({"ExistingUsers": []})
        user_df.to_csv(userbase, index=False)
    #turn on server and start listening
    server_socket.listen()
    #confirmation message server is running
    Log("server is listening for connections..." + str(sHost)+":"+str(sPort), logfilename)
    print("server is listening for connections..." + str(sHost)+":"+str(sPort))
    return server_socket


##UNTESTED BELOW HERE##
#Wire_to_Function(cSocket: socket,sList: socket List, onlineClients: Dict[key=socket] = username : string, loginFlag: boolean, database: String, logfilename: String): 
    #checks and decodes wire protocol version number (ensuring match to local one), operation code (ensuring validity), and remaining input length from client socket cSocket
    #if loginFlag is True, will only accept login opcode (3) on call
    #for a valid opcode, passes all necessary information to the corresponding server operation or records an exception
    #logs progress in text log file called logfilename
def Wire_to_Function(cSocket, sList=socket_list, onlineClients=online_clients, loginFlag=False, database=data, userbase=users, logfilename=log_name):
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
        #pick num of ops, rn 5
        if op_code_decoded > 5:
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
                Send_Message(cSocket, in_len_decoded, onlineClients, database, userbase, logfilename)
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
                Delete_Acct(cSocket, remaining_input, onlineClients, database, userbase, logfilename)
                Log("finished deleting account from " + str(cSocket), logfilename)
            #3: login
            case 3:
                remaining_input = cSocket.recv(in_len_decoded)
                Log("attempting logging in from " + str(cSocket), logfilename)
                Login(cSocket, remaining_input, sList, onlineClients, database, userbase, logfilename)
                Log("finished logging in for " + onlineClients[cSocket], logfilename)
            #4: list accounts
                Log("attempting account list retrieval from " + onlineClients[cSocket], logfilename)
                List_Accounts(cSocket, remaining_input, onlineClients, userbase,logfilename)
                Log("finished sending account list for " + onlineClients[cSocket], logfilename)
            #5: error
            case 5:
                remaining_input = cSocket.recv(in_len_decoded).decode('utf-8').strip()
                Log("recieved error from client" + onlineClients[cSocket], logfilename)
                Rec_Exception(ValueError, remaining_input, logfilename)
    #otherwise socket is broken in some way, nothing left to do
    except:
        return False


#Socket_Select(sSocket: socket, sList: socket List, onlineClients: Dict[key=socket] = username : string, database: String, logfilename: String): 
    #use select library to sort sockets into lists of sockets we have recieved data over, sockets with data ready to be sent, and sockets with errors on them
    #goes through each socket with data on it, accepting the new connection and logging in for a connection on the server socket sSocket
    #for any other data socket calls wire_to_function to execute local server operation
    #for socket with error, removes it from list of active sockets sList and from onlineClients dictionary
    #logs progress in text log file called logfilename, passes active user information and stored messages per offline user in database to functions that need it
    #all should be encased in an infinite loop for use
def Socket_Select(sSocket, sList=socket_list, onlineClients=online_clients, database=data, userbase=users, logfilename=log_name):
    #produces list of sockets:
        #that we have recieved data on (rsockets)
        #sockets ready for data to be sent (wSockets)
        #sockets with errors (eSockets)
    rSockets, _, eSockets = select.select(sList, [], sList)
    #go through sockets with information in them
    for rSocket in rSockets:
        #if server socket has content, we have a new connection
        if rSocket == sSocket:
            Log("found server communication, pending connection acceptance", logfilename)
            #accept connection
            cSocket, cAddr = sSocket.accept()
            Log("accepted connection from " + str(cAddr), logfilename)
            #should come with a login request, pass to function converter for handling
            b = Wire_to_Function(cSocket, sList, onlineClients, True, database, userbase, logfilename)
            #u_name false means communication failed in some way, stop and repeat process
            if not b:
                return False
        #otherwise existing socket is sending a non-connection operation
        else:
            #decode and do whatever operation sent via rSocket
            Log("recieved operation from socket " + str(rSocket), logfilename)
            b = Wire_to_Function(rSocket, sList, onlineClients, False, database, userbase, logfilename)
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


#Login(cSocket: socket, input: encoded bytearray to utf-8, sList: socket List, onlineClients: Dict[key=socket] = username : String, database: String, userbase: String, logfilename: String):
    #using communication over client socket cSocket, decodes username from encoded input, validates username for login
    #enforces username length cap of 256 characters
    #for new users, add to list of existing users in database
    #for returning users, looks for stored messages and sends them if they exist in database
    #for duplicate usernames or failure, login fails by returning false
    #logs progress in text log file called logfilename
def Login(cSocket, input, sList, onlineClients, database=data, userbase=users, logfilename=log_name):
    try:
        #decode input username, input already correct length
        username = input.decode('utf-8').strip()
        Log("username: " + username, logfilename)
        #enforce username length cap
        if len(username) > 256:
            username = username[:255]
        #if username already online, fail
        if username in onlineClients:
            return False
        #if username doesn't already exist offline, add to list
        user_df = pd.read_csv(userbase)
        Log("database successfully read for user " + username,logfilename)
        if username not in list(user_df["ExistingUsers"]):
            user_df = user_df.append({"ExistingUsers": username}, ignore_index=True)
        user_df.to_csv(userbase, index=False)
        #succeeded!, add to list of active sockets and dict online clients with the username
        sList.append(cSocket)
        onlineClients[cSocket] = username
        Log("added to socket list for user " + username, logfilename)
        #if username offline with stored messages, bring back and send those messages
        data_df = pd.read_csv(database)
        if username in list(data_df.columns):
            msgs = list(database[username])
            for msg in msgs:
                cSocket.send(msg)
            #delete that column from the dataset
            data_df = data_df.drop(username, axis='columns')
            Log("sent stored messages to " + username, logfilename)
        data_df.to_csv(database, index=False)
    except:
        Rec_Exception(ValueError, "Username could not be parsed from socket " + str(cSocket) + ". login will now fail.", logfilename)
        return False


#Msg_to_Wire(recip: String, msg: String, sender: String, logfilename: String):
    #constructs encoded message from msg with sender username (sender) to be sent in future function to recipient with username recip
    #returns message encoding
    #logs progress in text log file called logfilename
def Msg_to_Wire(recip, msg, sender, logfilename=log_name):
    #TODO: fix padding throughout
    #create byte array
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{str(wp_version):<{4}}".encode('utf-8'))
    #add opcode, in this case 0 (already a single byte)
    wire += (f"{str(0):<{1}}".encode('utf-8'))
    #add length of rest of input: 4+1+len(recip)+len(msg)
    l_recip = len(recip)
    l_msg = len(msg)
    l = 4+1+l_recip+l_msg
    wire += (f"{str(l):<{4}}".encode('utf-8'))
    #add byte for length of recipient username (already a single byte)
    wire += (f"{str(l_recip):<{1}}".encode('utf-8'))
    #add recipient username
    wire += (recip.encode('utf-8'))
    #add message
    wire += (msg.encode('utf-8'))
    #log wire having been built and return the completed wire
    Log("Wire for message reciept built to be sent by " + sender, logfilename)
    return wire


#Send_Message(cSocket: socket, inlen: int, onlineClients: Dict[key=socket] = username : string, database: String, logfilename: String):
    #decodes recipient username and message sent from client socket cSocket according to wire protocol using length of input inlen
    #if recipient online in onlineClients dictionary, encode message and send to recipient through their socket
    #if recipient offline, encode message and store it in csv file with name database
    #returns false on failure to send
    #logs progress in text log file called logfilename
def Send_Message(cSocket, inlen, onlineClients, database=data, userbase=users, logfilename=log_name):
    #decode recipient username and message according to wire protocol
    len_recip = int(cSocket.recv(1).decode('utf-8').strip())
    recip = str(cSocket.recv(len_recip).decode('utf-8').strip())
    msg = str(cSocket.recv(inlen-1-len_recip).decode('utf-8').strip())
    #get sender's username from live clients
    sender = onlineClients[cSocket]
    Log("recipient, message, and sender successfully retrieved from socket " + onlineClients[cSocket] ,logfilename)
    #if recipient does not exist, fail
    user_df = pd.read_csv(userbase)
    if recip not in list(user_df["ExistingUsers"]):
        return False
    #find recipient and send to them TODO (clunky)
    recip_socket_set = {i for i in onlineClients if onlineClients[i]==recip}
    recip_socket= cSocket
    for r in recip_socket_set:
        recip_socket = r
    #get converted message
    wire = Msg_to_Wire(recip,msg,sender,logfilename)
    data_df = pd.read_csv(database)
    #if recip online, send message
    if recip in onlineClients:
        recip_socket.send(wire)
    #otherwise offline, store in database for future send
    else:
        #if col for this user exists, add encoded message there
        if recip in list(data_df.columns):
            data_df = data_df.append({recip: wire}, ignore_index=True)
        #if it doesn't exist, insert a column with that addr
        else:
            data_df = data_df.insert(2, recip, [wire], True)
        #save dataframe to csv
        data_df.to_csv(database, index=False)


#Send_Error(cSocket: socket, eMsg: String, logfilename: String):
    #encodes error message according to wireprotocol and sends to client socket cSocket
    #logs progress in text log file called logfilename
def Send_Error(cSocket, eMsg, logfilename=log_name):
    #encode error with wire protocol function
    #create byte array
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{str(wp_version):<{4}}".encode('utf-8'))
    #add opcode, in this case 4 (already a single byte)
    wire += (f"{str(4):<{1}}".encode('utf-8'))
    #add length of message
    wire += (f"{str(len(eMsg)):<{4}}".encode('utf-8'))
    #add message
    wire += (eMsg.encode('utf-8'))
    #send encoded error
    Log("built error wire to send to client" + str(cSocket), logfilename)
    cSocket.send(wire)


#Delete_Acct(cSocket: socket, input: encoded byteArray to utf-8, onlineClients: Dict[key=socket] = username : String, database: String, logfilename: String):
    #decodes confirmatory username in input from client socket cSocket, ensures this matches the online username in the onlineClients dictionary
    #if it matches, account is deleted by removing username from list of existing users and from onlineClients dictionary
    #otherwise, records and sends an error that deletion failed
    #logs progress in text log file called logfilename
def Delete_Acct(cSocket, input, onlineClients=online_clients, database=data, userbase=users, logfilename=log_name):
    #decode confirmatory username
    confirm = input.decode('utf-8').strip()
    #ensure confirmatory username and cSocket username match
    if confirm == onlineClients[cSocket]:
        Log("deletion confirmed. Beginning account deletion process for " + confirm, logfilename)
        #send confirmation message
        #create byte array
        wire = bytearray()
        #first add protocol version number encoded to 4 bits
        wire += (f"{str(wp_version):<{4}}".encode('utf-8'))
        #add opcode, in this case 2 for delete
        wire += (f"{str(2):<{1}}".encode('utf-8'))
        msg = "account deleted. Client shutting down."
        wire += (f"{str(len(msg)):<{4}}".encode('utf-8'))
        wire += (msg.encode('utf-8'))
        user_df = pd.read_csv(userbase)
        lst = list(user_df["ExistingUsers"])
        lst = lst.remove(confirm)
        print(confirm)
        try:
            new_user_df = pd.DataFrame({"ExistingUsers": lst})
            new_user_df.to_csv(userbase, index=False)
        except:
            new_user_df = pd.DataFrame({"ExistingUsers": []})
            new_user_df.to_csv(userbase, index=False)
        data_df = pd.read_csv(database)
        #delete all stored messages for that account if the column exists (it shouldn't!)
        try:
            if data_df[confirm]:
                data_df = data_df.drop(confirm, axis='columns')
            data_df.to_csv(database, index=False)
        except:
            pass
        Log("deleted user from all databases")
        #remove from online clients database, active sockets and existing clients
        onlineClients.remove(cSocket)
    #otherwise, deletion won't occur. 
    else:
        Rec_Exception(ValueError, "deletion failed. Ensure that you send your username along with the deletion request.",logfilename)
        Send_Error(cSocket, "deletion failed. Ensure that you send your username along with the deletion request.",logfilename)


#Logout(cSocket: socket, input: encoded byteArray to utf-8, onlineClients: Dict[key=socket] = username : String, logfilename: String):
    #decodes confirmatory username in input from client socket cSocket, ensures this matches the online username in the onlineClients dictionary
    #if it matches, account is logged out by removing username from onlineClients dictionary
    #otherwise, records and sends an error that logout failed
    #logs progress in text log file called logfilename
def Logout(cSocket, input, onlineClients=online_clients, logfilename=log_name):
    #decode confirmatory username
    confirm = input.decode('utf-8').strip()
    #ensure confirmatory username and cSocket username match
    if confirm == onlineClients[cSocket]:
        Log("logout confirmed. Beginning account logout process for " + confirm, logfilename)
        #create byte array
        wire = bytearray()
        #first add protocol version number encoded to 4 bits
        wire += (f"{str(wp_version):<{4}}".encode('utf-8'))
        #add opcode, in this case 1 for logout
        wire += (f"{str(1):<{1}}".encode('utf-8'))
        msg = "account logged out. Client shutting down."
        wire += (f"{str(len(msg)):<{4}}".encode('utf-8'))
        wire += (msg.encode('utf-8'))
        cSocket.send(wire,logfilename)
        Log("sent logout confirmed message back to client")
        #remove from online clients database and active sockets
        onlineClients.remove(cSocket)
    #otherwise, logout won't occur. 
    else:
        Rec_Exception(ValueError, "logout failed. Ensure that you send your username along with the logout request.",logfilename)
        Send_Error(cSocket, "logout failed. Ensure that you send your username along with the logout request.",logfilename) 
    

#List_Accounts(cSocket: socket, input: String, onlineClients: Dict[key=socket] = username: String, database: String, logfilename: String):
    #generates list of existing usernames from database
    #converts list to an encoded message that is then sent to the client socket cSocket
    #logs progress in text log file called logfilename
def List_Accounts(cSocket, input, onlineClients=online_clients, userbase=users, logfilename=log_name):
    #grab accounts from dataset
    user_df = pd.read_csv(userbase)
    accounts = list(user_df["ExistingUsers"])
    #filter by input keyword (already decoded)
    ret_list = accounts
    if input.__contains__("*") and len(input) > 1:
        ret_list = filter(lambda usrnm: usrnm[:len(input)-2] == input[:len(input)-2], accounts)
    elif not input.__contains("*"):
        ret_list = filter(lambda usrnm: usrnm[:len(input)-1] == input, accounts)
    Log("retrieved existing users, sending to client " + onlineClients[cSocket], logfilename)
    #send accounts to client
    msg_accounts = "Existing accounts by username: \n"
    #create message with existing accounts
    for account in ret_list:
        msg_accounts += account + " "
    #convert to wire
    #create byte array
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{str(wp_version):<{4}}".encode('utf-8'))
    #add opcode, in this case 4 for list
    wire += (f"{str(4):<{1}}".encode('utf-8'))
    wire += (f"{str(len(msg_accounts)):<{4}}".encode('utf-8'))
    wire += (msg_accounts.encode('utf-8'))
    cSocket.send(wire)


#server execution
#clear server log
open(log_name, 'w').close()
#startup server
server_socket = Start_Server(server_host, server_port, log_name, data, users, False)
#add server socket to list of sockets for selection
socket_list = [server_socket]
#infinitely select through sockets
while True:
    Socket_Select(server_socket, socket_list, online_clients, data, users, log_name)