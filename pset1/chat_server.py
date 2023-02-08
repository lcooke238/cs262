#imports

#server startup function
    #setup server socket
    #bind to host and port
    #access database with users and stored messages
        #ensure reachable, if not, throw warning and create a new one
    #turn on server and start listening


#accept client function
    #should get login username as first contact
    #check version number of wire protocol
        #ensure it is what you expect, if not throw versionError
    #query fed username:
        #if exists and is offline
            #bring online
            #communicate success
            #feed client stored messages
            #delete stored message
            #repeat until storage is empty
        #if exists and is online
            #BAD BAD BAD throw unique user warning to them and prevent login
        #if does not exist anywhere
            #create in online category
            #communicate success


#message handling function
    #should recieve message with sender username, recipient username, and message
        #ensure all three components arrived non-empty, if not return emptyField error to sender
        #validate sender username is online, if not return invalidAccount error
        #validate recipient username exists, if not return invalidRecipient error
            #if it does, store where it is (online or offline)
    #if recipient online:
        #send message in proper format to that client
    #if recipient offline:
        #store message for them in database


#send error function
    #encode error with wire protocol function
    #send encoded error


#recieve error function
    #decode error with wire protocol function
         #if either field is blank, display failedErrorTransmission error
    #display decoded error
    

#delete account function
    #should recieve sender username
        #ensure sender username exists and is online, if not return faultyCommunication error
    #otherwise, communicate warning to sender about implications (losing all messages, getting logged out, etc.)
        #communication also includes a generated key stored locally on server array
    #if user communicates a delete back with the generated key, then the account will be deleted. (communicate success)
    #any other communication with delete operation will cancel the deletion.


#logout function
    #should recieve sender username
        #ensure sender username exists and is online, if not return faultyCommunication error
    #move user to offline in database
    #communicate success


#database query function (input query type)
    #make query of choice
    #save database if succeeds
    #return result


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
