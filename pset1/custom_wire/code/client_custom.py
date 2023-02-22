#imports
import socket
import warnings
import sys
import errno
import os

#constants
client_host = "127.0.0.1"
client_port = 1234
log_name = "../logs/client_log.txt"
wp_version = 0


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


#Display_Message(msg: String, logfilename: String):
    # given a message msg, displays message to user and logs it in text file log called logfilename
def Display_Message(msg, logfilename=log_name):
    print(msg)
    Log(msg, logfilename)


#Start_Client(cHost: String, cPort: int, logfilename: String):
    #asks user for a valid username until recieving one
    #creates client socket
    #sends the encoded login username to the server through the client socket
    #logs all progress in log text file called logfilename
    #returns client socket and username in a pair
def Start_Client(cHost, cPort, logfilename=log_name):
    #grab user input for username before starting connection
    user_ok = False
    user = ""
    while not user_ok:
        user = input("Type a unique username, note all spaces and commas will be removed: ")
        #ensure username is within a given limit before continuing
        #remove spaces and commas
        user = user.strip()
        user.replace(" ", "")
        user.replace(",", "")
        if user != "" and len(user) < 20:
            user_ok = True
            continue
        #otherwise username invalid, display problem and re-ask
        Display_Message("input username empty or too long, please try again.", logfilename)
        continue

    #create socket and connect to server socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((cHost, cPort))
    Log(f"connected to {cHost}.{cPort}", logfilename)
    # #prevent reciving block
    client_socket.setblocking(False)
    #send converted username to server
    wire = Login_Wire(user, wp_version, logfilename)
    client_socket.send(wire)
    Log("sent login wire for user: " + user, logfilename)
    return client_socket, user


#def Login_Wire(user: String, wp_version: int, logfilename: String):
    #converts a given username for login to sendable wire
    #returns wire to be sent in later function, logs progress in text log called logfilename
def Login_Wire(user, wp_version=wp_version, logfilename=log_name):
    wire = bytearray()
    #add wire version number
    wire += (f"{str(wp_version):<{4}}".encode('utf-8')) 
    #add opcode for login (3)
    wire += (f"{str(3):<{1}}".encode('utf-8'))
    #add length of username
    wire += (f"{str(len(user)):<{4}}".encode('utf-8'))
    wire += (user.encode('utf-8'))
    Log("wire for client login created", logfilename)
    return wire 


#input management
    #return false when loop should start over
def In_Manager(cSocket, user, logfilename=log_name):
    #get user input
    cmd = input(f"{user} > ")
    #Send: if command is in proper send format, activate send protocol
    if (cmd[0:5] == "\\send") and cmd.__contains__(","):
        args = cmd[6:].strip()
        arg_list = args.split('\,')
        if len(arg_list) != 2:
            Display_Message("Improper command format. Did you add an extra \",\"?")
            return False
        msg = arg_list[0].strip()
        usrnm = arg_list[1].strip()
        if msg == "" or usrnm == "":
            Display_Message("Improper command format. Did you leave an argument blank?")
            return False
        #now all formatting should be okay to get request to server
        Send_Message(cSocket, usrnm, msg, logfilename)
        return False

    #Logout: if command is in proper logout format, activate logout protocol
    elif cmd[0:7] == "\\logout":
        #verify logout input
        verify = input("are you sure you want to log out? Type yes to continue: ")
        if verify.strip() == "yes":
            #call logout function
            Logout(cSocket, user, logfilename)
            return False
    
    #Delete: if command is in proper delete format, activate delete protocol
    elif cmd[0:7] == "\\delete":
        #verify delete input
        verify = input("are you sure you want to delete this account? Type yes to continue: ")
        if verify.strip() == "yes":
            #call delete function
            Delete(cSocket, user, logfilename)
            return False

    #List: if command is in proper list format, activate list protocol
    elif cmd[0:5] == "\\list" and cmd[6:].strip() != "":
        arg = cmd[6:].strip()
        ListUsr(cSocket, arg, logfilename)
        return False

    #Help: if command is in proper help format, activate help
    elif cmd[0:5] == "\\help":
        Help(user,logfilename)
        return False
    
    elif cmd[0:6] == "\\clear":
        # Clearing the Screen
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    #empty input, do nothing
    elif cmd.strip() == "":
        return False

    #otherwise, tell user you don't understand their command and to retry
    else:
        Display_Message("Improper command syntax. Type \"\\help\" for instructions on how to use the interface.", logfilename)
        return False


#IO management loop
    #return False when loop should start over
def IO_Manager(cSocket, user, logfilename=log_name):
    In_Manager(cSocket, user, logfilename)
    try:
        #Get first 4 bytes for wire protocol version number
        protocol_version = cSocket.recv(4)
        #if we recieve nothing, socket has been shut down/closed on the other end, so we end the call.
        if not len(protocol_version):
            return False
            #Display_Message("Connection Closed by Server. Shutting Down.",logfilename)
            #sys.exit()
        #check for the expected protocol version number
        protocol_version_decoded = int(protocol_version.decode('utf-8').strip())
        if protocol_version_decoded != wp_version: 
            #get the wrong version, log the error and close the connection
            Rec_Exception(ValueError, "Wire Protocol version does not match. Client expected version " + str(wp_version) + ", got " + str(protocol_version_decoded),logfilename)
            Display_Message("Wire protocol version mismatch. Shutting down.",logfilename)
            sys.exit()
        #otherwise, version is good and we can recieve the operation code
        op_code = cSocket.recv(1)
        op_code_decoded = int(op_code.decode('utf-8').strip())
        #check for invalid op code and communicate faulty operation if found
        #pick num of ops, rn 5
        if op_code_decoded > 5 or op_code_decoded == 3:
            Rec_Exception(ValueError, "Operation Code Faulty. Please ensure that your wire protocol is converting your request properly.",logfilename)
            return False
        #grab rest of input length and input from socket with default size in wire protocol
        in_len_decoded = int(cSocket.recv(4).decode('utf-8').strip())
        #for the proper operation code, pass rest of input to the respective function
        match op_code_decoded:
            #0: display message from another user
            case 0:
                Log("message recieved. Parsing to display...",logfilename)
                l_usr = int(cSocket.recv(1).decode('utf-8').strip())
                usr = cSocket.recv(l_usr).decode('utf-8').strip()
                msg = cSocket.recv(in_len_decoded-l_usr-1).decode('utf-8').strip()
                Display_Message(f"{usr} > {msg}", logfilename)

            #1: logout communication from server
            case 1:
                Display_Message("Logout Successful. Shutting Down.", logfilename)
                sys.exit()
                
            #2: Delete communication from server
            case 2:
                Display_Message("Deletion Successful. Shutting Down.", logfilename)
                sys.exit()
                
            #4: display account list from server
            case 4:
                lst = cSocket.recv(in_len_decoded).decode('utf-8').strip()
                act_lst = lst.split(" ")
                Display_Message("users from query: ", logfilename)
                if not act_lst == ['']:
                    for act in act_lst:
                        Display_Message(act + ", ",logfilename)
               
            #5: error from server
            case 5:
                emsg = cSocket.recv(in_len_decoded).decode('utf-8').strip()
                Display_Message(emsg, logfilename)
    #socket potentially broken
    except IOError as IOE:
        if IOE.errno != errno.EAGAIN and IOE.errno != errno.EWOULDBLOCK:
            Rec_Exception('Reading error: {}. Shutting Down.'.format(str(IOE)),logfilename)
            Display_Message('Reading error: {}. Shutting Down.'.format(str(IOE)),logfilename)
            sys.exit()
        return False
    #otherwise socket is seriously broken, gotta kill the client
    except Exception as E:
        Rec_Exception('Error: {}. Shutting Down.'.format(str(E)),logfilename)
        Display_Message('Error: {}. Shutting Down.'.format(str(E)),logfilename)
        sys.exit() 

#Help(user: String, logfilename: String):
    #Displays the different commands that the user can use and their syntax.
    #Logs the display in the text log file called logfilename
def Help(user, logfilename=log_name):
    msg = "Welcome to the chat service, "+user+"""! Here is a list of commands available to you and their syntax: \n
    \send msg\, usrnm -- sends the message msg to the person with username usrnm. \n
    \logout -- logs you out of your account. Client will shutdown after. \n
    \delete -- deletes your account. Client will shutdown after. \n
    \list ltrs -- provides a list of existing accounts that start with the string ltrs.
                  Use * to get a list of every existing account. \n
    \clear -- clears console display thus far. \n
    \help -- displays the different commands and their syntax.
    """
    Display_Message(msg, logfilename)


# send msg protocol
def Send_Message(cSocket, user, msg, logfilename=log_name):
    #encode message
    wire = Msg_to_Wire(msg, user, logfilename)
    #send message over socket
    cSocket.send(wire)
    #log send
    Log("message sent to " + user, logfilename)


# msg conversion fn
def Msg_to_Wire(msg, usrnm, logfilename=log_name):
    #encode version number
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{wp_version:<{4}}".encode('utf-8'))
    #add opcode, in this case 0 (already a single byte)
    wire += (f"{str(0):<{1}}".encode('utf-8'))
    #add length of rest of input: 4+1+len(recip)+len(msg)
    l_recip = len(usrnm)
    l_msg = len(msg)
    l = 4+1+l_recip+l_msg
    wire += (f"{str(l):<{4}}".encode('utf-8'))
    #add byte for length of recipient username (already a single byte)
    wire += (f"{str(l_recip):<{1}}".encode('utf-8'))
    #add recipient username
    wire += (usrnm.encode('utf-8'))
    #add message
    wire += (msg.encode('utf-8'))
    #log wire having been built and return the completed wire
    Log("Wire for message reciept built to be sent", logfilename)
    return wire


#logout function
def Logout(cSocket, usrnm, logfilename=log_name):
    #encode version number
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{wp_version:<{4}}".encode('utf-8'))
    #add opcode, in this case 1 (already a single byte)
    wire += (f"{str(1):<{1}}".encode('utf-8'))
    #add len of usrnm
    wire += (f"{str(len(usrnm)):<{4}}".encode('utf-8'))
    #add usrnm
    wire += (f"{usrnm:<{4}}".encode('utf-8'))
    Log("Wire for logout built to be sent", logfilename)
    #send message over socket
    cSocket.send(wire)
    #log send
    Log("logout message sent", logfilename)
    #kill client
    sys.exit()


#delete function
def Delete(cSocket, usrnm, logfilename=log_name):
    #encode version number
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{wp_version:<{4}}".encode('utf-8'))
    #add opcode, in this case 2 (already a single byte)
    wire += (f"{str(2):<{1}}".encode('utf-8'))
    #add len of usrnm
    wire += (f"{str(len(usrnm)):<{4}}".encode('utf-8'))
    #add usrnm
    wire += (f"{usrnm:<{4}}".encode('utf-8'))
    Log("Wire for delete built to be sent", logfilename)
    #send message over socket
    cSocket.send(wire)
    #log send
    Log("delete message sent", logfilename)
    #kill client
    sys.exit()


#list users fn
def ListUsr(cSocket, arg, logfilename=log_name):
    #encode version number
    wire = bytearray()
    #first add protocol version number encoded to 4 bits
    wire += (f"{wp_version:<{4}}".encode('utf-8'))
    #add opcode, in this case 4 (already a single byte)
    wire += (f"{str(4):<{1}}".encode('utf-8'))
    #add len of arg
    wire += (f"{str(len(arg)):<{4}}".encode('utf-8'))
    #add arg
    wire += arg.encode('utf-8')
    Log("Wire for list built to be sent", logfilename)
    #send message over socket
    cSocket.send(wire)
    #log send
    Log("listUsr message sent", logfilename)



#client execution
if __name__ == "__main__":
    #clear client log
    open(log_name, 'w').close()
    #setup client
    cSocket, username = Start_Client(client_host, client_port, log_name)
    #display how to access instructions
    Display_Message("type \help to see instructions. Press Enter to look for buffered returns.", log_name)
    #run IO management until kill
    while True:
        #run IO manager until death
        IO_Manager(cSocket, username, log_name)