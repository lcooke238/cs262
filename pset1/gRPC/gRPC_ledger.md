# COMPSCI 262 PSET 1: gRPC Engineering Ledger

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

This one behaves a little differently to our manual socket implementation. I don't fully understand
the streaming system with my gRPC testing, so I'm going to handle essentially all send messages in two stages:
sender -> server, and then receiver <- server. To handle this it seems like I could set up two sets of stubs, but
I'm going to keep it simple - the sender just sends data the server. The receiver (if online) will just frequently
request for messages from the server. I'll go into more detail on this shortly.

**Server Skeleton**:
1. bind to a host and port.
2. Add the gRPC handler to the server with some number of workers (threads).
3. turn on the server and start listening.
4. For any RPC request, update the database as appropriate and return the information required for the request.
5. On shutdown and startup, ensure all users are set to offline correctly to ensure no user gets stuck in deadlock
    on server shutdown or error (fail nicely).
6. Return any errors to the client via the errormessage in all the Reply types in the protos
7. All requests to the database must be threadsafe - two of the same user should not be able to log in at the same time
    messages go missing, logout but remain offline due to a simultaneous login etc. Functions making changes to the 
    data should lock. Some other functions (e.g. list) can go without locking.

**Client Skeleton**
The client will run in two distinct parts:

1. The main thread:
a. the main thread waits for user input to log in, and will log a user in upon being provided
    a valid username that is not currently logged in elsewhere.
b. It then loops until a 1) server shutdown, 2) \quit waiting for commands
c. Upon a command being entered, we check if the command is valid, else we loop
d. If the command is valid, we hand to the appropriate function, wait for it to return before looping again

2. The listener thread:
a. The listener thread blocks until a user is logged in (via a condition variable notification)
b. Once a user is logged in, it polls the server for unread_messages constantly via GetMessages.
c. For any message it finds, it displays the message
d. If a user logs out, it goes back to blocking and waiting for the condition variable notification.


**Error Types**:
1. *ServerShutdown*: Impossible to recover from for the client, this simply shuts down the client instantly as there is nothing they can do without the server.
<br>

2. *ForcedExit*: Exit gracefully if user attempts to manually kill the program (e.g. CTRL + C) by ensuring they get logged out before shutting down. 
<br>

**Test Suite Ideas**
1. Run the server separately, and have a testing file that simulates one or more users interacting with the server
2. Test via what output the client and/or server receives.
3. Or test via querying the database to check operations were performed correctly.

## Changes & learning points along the way

### 20-22 Feb

	-> Added testing suite

	-> Added a few safety checks e.g. message length as gRPC packets capped at 4MB, try excepts to catch most errors
	more gently.

### 19 Feb

	-> Added locking to database to ensure thread safety.

	-> Also realized I was double pulling data by pulling messages upon login and upon thread startup, not an issue now with locking but removed the redundant message pull from the login functionality.

### 18 Feb

	-> Added functionality to crash more gently, including handling CTRL + C and server shutdown.

### 17 Feb

	-> Added multithreading to the client to listen.

	-> Pull messages upon login added.

### 16 Feb

	-> Restructured folders

	-> Created the bulk of the basic functions and protos