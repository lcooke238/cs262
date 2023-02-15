# COMPSCI 262 PSET 1: Engineering Ledger
## Lauren Cooke

## Assignment Synthesis, What we need To do:
*Full spec on canvas if needed*
1. Design a "simple chat application" (client/server app) **by designing a wire protocol** with the following functions:
	- Create an account. You must supply a unique user name.
	- List accounts (or a subset of the accounts, by text wildcard)
	- Send a message to a recipient. If the recipient is logged in, deliver immediately; otherwise queue the message and deliver on demand. If the message is sent to someone who isn't a user, return an error message
	- Deliver undelivered messages to a particular user
	- Delete an account. You will need to specify the semantics of what happens if you attempt to delete an account that contains undelivered message.

	- must use transfer buffers and sockets of our own design bw the machines
	- must write a spec of the wire protocol, and the server must use that protocol
	- must be possible for multiple clients to connect to the server at the same time (with a single instance of the server only)
	- public github repo with a README that has instructions on how to setup the client and server so that the system will run
	- legal languages: python, C, C++, Java, C#
	- keep a notebook (this one!) for decision making

Logistics
	- turn in a link to the repo or a tar/zip file of the final product
	- DO NOT INCLUDE NAME in the files

2. re-implement or alter the app built in part 1 using gRPC
	- in notebook, add comparisons over the complexity of the code, performance differences, and buffer sizes being sent back and forth


## Brainstorming
**Server Skeleton**:
1. Check version number of wire protocol.
	- If we cannot handle this version, return a *FatalError*
2. bind to a host and port
	- possible error here? TBD
3. turn on the server and start listening
4. recieve client communication to login, ask for a username (OK to assume first message is a login message)
5. recieve username, ensure it is unique, communicate success
	- either create client account or log back into client account
6. maintain userbase that is online and separate one that is offline (and maintain message queues for offline!).
7. listen for communication from logged-in client with message and a username
	- verify that both are present in the correct format spec, if not return a message error explaining what part is wrong if possible
	- verify message sent in correct format is being sent to a valid account, if not send back an error to the client
8. upon proper message receipt, determine if user is online or not.
	- if online, send message 
	- for offline, queue the messages they get while offline until next login to then send
9. listen for account deletion message from client with username.
	- if said user has undelivered message, indicate this to client who wants to delete and inform them that these messages will be lost, ensure they wish to proceed. 
	- if so, delete account from server along with all stored messages
10. take logout requests
	- account still exists, however it is now offline, meaning any messages sent will be queued

**Client Skeleton**
1. login with valid user or new one to create new account
	- verify correct formatting and content (aka it exists) before send, if not give error
2. upon login, check with server for any logged messages and display them if applicable
3. send messages in correct format to another account
	- verify correct formatting
	- worth keeping local lists to verify users locally?
4. message reciept: display message to user
5. send logout request
	- need to close sockets upon logout



**Error Types**:
1. *FatalError*: Impossible to recover from, kills all components, will likely be common to server stuff because we will only have a single server.
<br>

2. *LocalError*: Error specific to a given instance/client that cannot be recovered, rest of system remains unaffected. Will only kill the problematic component. Will likely exist with specific clients.
<br>

3. *Warning*: problem occurred within running system, does not affect overall system functionality (ie. if we can identify an indicator of a faulty packet, can give someone a warning?)

**Test Suite Ideas**
1. *message format error*: user fails to provide a message and/or username in the format specified
	- if possible, (aka format is correct but location for a piece of information is blank, create more specific problems errors to share)
	- verifiable both on client and server end (do once on client for input check, once on server for travel check)
	<br>

2. can duplicate above for all possible message over server formats
<br>

3. more generalized u gave me nonsense doesn't bind to message type


## Stuff I have considered and left behind
1. Don't need to verify your own existence: 
a. loopback interface. Is this good design? --> DONT DO THAT YOU HAVE A THREAD THEREFORE YOU ARE
<br>

2. Don't need to send back message to the client to verify correctness --> overkill
<br>

3. Multithreading a good idea, but not necessary for this assignment:
a. All of this occurs on a single server, therefore upon receiving a request of any kind, the server should multithread this process and keep a listening channel open at all times. --> not worthwhile for this assignment, single thread ok
<br>

4. Storing whether or not a user is online externally is dumb, because that concept dissappears if the server goes down. Instead, only use database to store unsent messages (ie. column per offline user)
- instead maintain that locally on the server script


## Office Hour Wisdom
okay for everything to be single threaded, start with single threaded server bc allows for more straightforward network debugging (esp in python not really worth it)
- message over network format:
	- version number
	- (separate with byte for length of element before it)
	- wildcard compatability of some sort needed (getting groups of accounts by some sort of exp with a communication)



## Pseudocode
### Server
```
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
```

### Client
```
#imports

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
```


## Errors
1. *VSCode module installation problem*: To add libraries that vs code will be happy with, type the following in the terminal:
```
python3 -m pip install {new_module}
```
<br>

2. *text file reading and writing*: despite flushing after every write, my log text file will not display a write until I close the file and re-open it. I looked around on line for a means of debugging this, and the only advice I could find was to open the file for appending when writing, and open the file for reading when I wanted to read.
<br>

3. *pandas csv reading*: a dataframe is considered empty if it has header content, and converting to a csv will add an index column by default. To disable this, set 
```index=False```



## Testing Wisdom
I have found that a good workflow for me has been to break down each part of the server and client into functions. I then attempt to implement a function, followed by writing a test suite for said function. I run the tests one at a time, checking to see if they work as I expect, and fixing my mistakes as I go. 


## Wire Protocol (OH 2/10)
I decided to use a socket select protocol rather than a threading one to avoid any problems with partial failure and dataset locking for multiple threads of the server accessing a dataset at once. My design for the protocol itself works like this:

1. first 4 bytes (constant) represent the wire protocol version number. Upon reciept, a server and client will always check that this version number is what it expects, otherwise it will log the problem on the recieving side and close the socket. 
    - I chose to close the socket after logging the problem locally because we have no means of properly communicating the error back to the sender with a faulty wire protocol. 
2. next 1 byte (constant) represents the operation code. The operations are as follows:
    - 0: send a message to another user
        - next 4 bytes (constant) represents the length of the rest of the input to recieve (i)
        - next 1 byte (constant) represents the length of the username of the recipient (u)
        - next u bytes represents the username of the recipient
        - next i-1-u bytes represent the message
    - 1: logout
        - next 4 bytes (constant) represents the length of the rest of the input to recieve
        - rest of input represents the confirmation keyword to ensure opcode reciept wasn't a mistake
    - 2: delete
        - next 4 bytes (constant) represents the length of the rest of the input to recieve
        - rest of input represents the confirmation keyword to ensure opcode reciept wasn't a mistake
    - 3: login
        - next 4 bytes (constant) represents the length of the rest of the input to recieve
        - rest of input represents the username for the login
    -4: list accounts
        - next 4 bytes (constant) represents length of rest of input
        - rest of input represents the keyword to filter list by
    - 5: error/exception
        - next 4 bytes (constant) represents the length of the rest of the input to recieve
        - rest of input represents the error message to be used

Options:
1. have some kind of delimiter between portions of the protocol to read until this thing
    - tough bc have to find char u will never use
2. part of WP, at beginning of every field the length of that field
    - have pt that starts with 4 byte int as version number
    - next field may be a 32bit int indicating length of entire message (to know when ur done)
    - next part could be len of first field if u don't know already (ie. opcode)
    - mostly sending strs, can either have them all be the same len (x chars upper lim, if less then that pad w blanks)
        - or, could have 1st few chars be the length of number of chars in str
        - parse len, then read num of chars indicated therein
    - can repeat above per len
        - worth having separate opcode for sending lots of msgs at once

    - socket select (has gr8 tutorial)
    - get bytes on recieve from whatever socket you pick
    - parse the bytes you recieve
        - once u know opcode via parsing, know the method u will need (pass in remaining byte flow --> then have methods parse the rest according to that method)
        - finish and return:
            - hand in socket with return info, 
            - if u recieve 0, socket is dead, so close it and get rid of thread


## Client Spec
Within spec to block outputs while waiting for an input from the user, so I will do this. However, I will also add a function local to the client to just display messages immediately upon reciept. I will also add an escape key, so that a user can get out of this mode when they wish to.