#imports
import socket
import pandas as pd
import warnings

#constants
server_port = '127.0.0.1'
server_host = 8080
wire_protocol_version_number = 2
server_socket = None
#logfilename = 'server_log.txt'
#data_df = pd.read_csv('data.csv')


#Log(logfilename, msg): records input msg in input log with name logfilename
def Log(logfilename, msg):
    with open(logfilename, 'a') as log:
        log.write(msg + '\n')
        log.flush()


#Rec_Exception(eName, eMsg, log): display exception to server console and logs it
def Rec_Exception(eType, eMsg, logfilename):
    #handle warnings
    if eType == Warning:
        warnings.simplefilter("ignore", UserWarning)
        #print warning to server
        warnings.warn(eMsg)
        #log warning
        Log(logfilename, eMsg)


# #Start_Server(): startup server, open dataset, and begin listening for client connections
def Start_Server(sHost, sPort, logfilename, datasetname):
    #setup server socket
        #TODO: add unique wire protocol here
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((sHost, sPort))
    #try to access database with users and stored messages
    #TODO: add faulty format handling
    try: 
        data_df = pd.read_csv(datasetname)
        if data_df.empty:
            #if reachable and empty, throw warning
            Rec_Exception(Warning, 'EmptyDatasetWarning: Input message and client dataset is empty. Did you select the correct file?',logfilename)
    #access failed, record exception and create new dataset to use
    except:
        Rec_Exception(Warning, 'InvalidDatasetWarning: input dataset invalid, creating a new dataset for server to use',logfilename)
        #create new dataset
        new_df = pd.DataFrame({'Online':[], 'Offline':[]})
        new_df.to_csv(datasetname, index=False)

    #turn on server and start listening
    server_socket.listen()
    #confirmation message server is running
    Log(logfilename, "server is listening for connections...")


#TODO: accept client function
# def Accept_Client(ssocket, input):
#     #should get login username as first contact
#     #check version number of wire protocol
#         #ensure it is what you expect, if not throw versionError
    
#     while True:
#         #accept client passed through server socket
#         csocket, addr = ssocket.accept()
#         #confirmation message of connection acceptance
#         print("accepted connection from {addr}")
#         #query fed username:

#             #if exists and is offline
#                 #bring online
#                 #communicate success
#                 #feed client stored messages
#                 #delete stored message
#                 #repeat until storage is empty
#             #if exists and is online
#                 #BAD BAD BAD throw unique user warning to them and prevent login
#             #if does not exist anywhere
#                 #create in online category
#                 #communicate success


# #TODO: message handling function
# def Handle_Message():
#     #should recieve message with sender username, recipient username, and message
#         #ensure all three components arrived non-empty, if not return emptyField error to sender
#         #validate sender username is online, if not return invalidAccount error
#         #validate recipient username exists, if not return invalidRecipient error
#             #if it does, store where it is (online or offline)
#     #if recipient online:
#         #send message in proper format to that client
#     #if recipient offline:
#         #store message for them in database


# #TODO: send error function
# def Send_Error():
#     #encode error with wire protocol function
#     #send encoded error


# #recieve error function
# def Recieve_Error():
#     #decode error with wire protocol function
#          #if either field is blank, display failedErrorTransmission error
#     #display decoded error
    

# #delete account function
# def Delete_Acct():
#     #should recieve sender username
#         #ensure sender username exists and is online, if not return faultyCommunication error
#     #otherwise, communicate warning to sender about implications (losing all messages, getting logged out, etc.)
#         #communication also includes a generated key stored locally on server array
#     #if user communicates a delete back with the generated key, then the account will be deleted. (communicate success)
#     #any other communication with delete operation will cancel the deletion.


# #logout function
# def Logout():
#     #should recieve sender username
#         #ensure sender username exists and is online, if not return faultyCommunication error
#     #move user to offline in database
#     #communicate success


# #TODO: database query function (input query type)
# def Query():
#     #make query of choice
#     #save database if succeeds
#     #return result


# #TODO: msg to wire protocol function (add toggle bw manual and gRPC)
# def Msg_To_Wire():
#     #given input of all required pieces for communication:
#         #version number
#         #operation
#         #content
#         #More stuff??
#     #convert input to output as specified by wire protocol
#     #return this result


# #TODO: wire protocol to msg function (add toggle bw manual and gRPC)
# def Wire_To_Msg():
#     #given bit string
#     #check wire protocol version number is correct
#         #if not, report versionError and inform client
#     #convert according to wire protocol to message
#     #grab operation from request
#     #call said operation defined above
