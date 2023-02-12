#imports
import socket
import select

#constants
client_host = "127.0.0.1"
client_port = 1234

#TODO client socket creation function


#TODO Login protocol, subfunctino of client socket creation


#TODO Socket selection

#connect to server/login function
    #initialize state vars as 0
    #setup client socket
    #bind to host and port
    #encode login message according to wire protocol
    #send message to server
    #wait for response from server:
        #if responds with success, move on/function is over (for accts coming back online those messages will be sent by server already)
        #if responds with fail, raise invalidUsername exception and re-request user to login
        #if this takes longer than 5 minutes, raise timeOut error and kill client?


#recieve message function
    #should have message and sender username from input
        #ensure both fields are non-empty
            #if either is empty, return failedTransmission error to server
        #display message coming from sender username 


#send message function
    #encode message and usernames of interest with wire protocol function
    #send encoded message to server


#logout function
    #encode logout request with your username using wire protocol function
    #send encoded request to server
    #indicate locally that we are waiting for logout response with state var
    #get logout response from server, activate lower part of fn with state var:
        #if success, display logout succeeded, wait 5s, and kill client responsibly
        #if fail, display logoutError


#delete account function
    #encode logout request with your username using wire protocol function
    #send encoded request to server
    #indicate locally that we are waiting for delete response with state var
    #get response from server:
        #if success, display deletion warning and grab key
            #prompt user for confirmation letter
                #if input is confirmation letter, encode and send delete with key and confirmed state active, update local state var
                #if input is anything else, set state back to 0, tell user delete was cancelled, and communicate cancellation to server
            #get response from server, activate this part with extra state var:
                #if success, display delete succeeded, wait 5s, and kill client responsibly
                #if fail, display deleteConfirmError
        #if fail, display deleteError
        

#send error function
    #encode error with wire protocol function
    #send encoded error to server


#recieve error function
    #decode error with wire protocol function
        #if either field is blank, display failedErrorTransmission error
    #display decoded error


#msg to wire protocol function (add toggle bw manual and gRPC)
    #given input of all required pieces for communication:
        #version number
        #operation
        #content
        #More stuff??
    #convert input to output as specified by wire protocol
    #return this result


#wire protocol to msg function (add toggle bw manual and gRPC)
    #given bit string
    #check wire protocol version number is correct
        #if not, report versionError and inform client
    #convert according to wire protocol to message
    #grab operation from request
    #call said operation defined above