# COMPSCI 262 PSET 3: Engineering Ledger

## Assignment Synthesis, What we need To do:
* Take one of the two implementations you created for the first design exercise (the chat application) and re-design it so that the system is both persistent (it can be stopped and re-started without losing messages that were sent during the time it was running) and 2-fault tolerant in the face of crash/failstop failures. In other words, replicate the back end of the implementation, and make the message store persistent.

* The replication can be done in multiple processes on the same machine, but you need to show that the replication also works over multiple machines (at least two). That should be part of the demo.

* As usual, you will demo the system on Demo Day III (April 10). Part of the assignment is figuring out how you will demo both the new features. As in the past, keep an engineering notebook that details the design and implementation decisions that you make while implementing the system. 

## Design brainstorming
For this assignment, our gRPC implementation from pset 1 already is persistent, as it stores all messages not already successfully sent to a given client in a SQL database. This way, if the server crashes at any point, those messages can be successfully sent on a restarted server to the clients of interest. Our first major design choice here comes with our interpretation of the spec of this assignment does not require that we store all successfully sent messages, as these were already recieved by the user and storing them all over time would take up too much space. 

The next part of this assignment was to add replication to make our system 2-fault tolerant, allowing our chat server to stay running if some piece (either a client or a server) were to fail in some way. We also know that the replication will need to work over multiple machines, meaning that if some part failed on one machine, we could bring it back without failure on another. Some ideas for the server:
- instantiating a client will include checking if a server replica on a non-server computer exists. If it doesn't one will be made on the client machine (bad, running a server on the client is intrusive).
- maintaining a list of server backups in a set order, using the server at the front and every time the server gets an update of state, the server will send its updates to its backup, which will send to its backup (three backups total, like a chain mechanism) OR the front server is aware of all backups and it simply distributes to all the backups itself (more like a tree).
- if no backups nor the current server work (ie. network failure for everyone), handle shutdown comfortably for everyone.


## Demo Ideas
To properly demo our new features, we were thinking about doing the following:
- *persistence*: we would run an instance of the server and clients on multiple machines, send some messages that aren't recieved by a client (ie. sent to a logged out client) and throw them all on airplane mode to disrupt the connection to everyone and cause shutdown. Then, bring the entire system back up. Login to client who will recieve the stored messages, and show how they were stored!
- *replication*: get an instance of the machine running with two servers and two clients. Kill the first server instance, and show how it switches to the backup. 

##Server Skeleton

Giving a high level idea of what our server implementation does:
1. Has to be configured to run internally or externally
2. Takes in an id and uses it to bind to a host and port.
3. Sets all users offline in its local data to ensure on server restarts nobody is logged in.
4. Add the gRPC handler to the server with some number of workers (threads).
5. turn on the server and start listening.
6. Take in a set of backup information. It stores all servers given to it (in `other_servers`), and sets any with a higher id than itself as a potential backup in `backups`.
7. Once all servers are up and enter is hit, it connects to all other servers and checks their clock information (from a previous shutdown). It finds the server with the highest clock, deletes all of its local data and copies theirs across to their local data. 
8. It then begins its life as a server, simply waiting for `grpc` connections.
9. For any RPC request, update the database as appropriate and return the information required for the request.
10. Instantiate a `ServerWorker` object, which connects to each backup one at a time and updates their databases as appropriately too. 
11. On shutdown and startup, ensure all users are set to offline correctly to ensure no user gets stuck in deadlock
    on server shutdown or error (fail nicely).
12. Return any errors to the client via the errormessage in all the Reply types in the protos
13. All requests to the database must be threadsafe - two of the same user should not be able to log in at the same time
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

Note that upon first connecting to a server, the client runs `self.attempt_setup_backups()` - this calls a function in the stub to pull all the backups that the server the client is connected to is aware of. This ensures that even if the server goes completely offline, the client is aware of other backups and can attempt to connect to another server, which it does as soon as it gets nothing back from a server via `self.attempt_backup_connect()`, and re-runs the latest command on that server.


**Error Types**:
1. *ServerShutdown*: Impossible to recover from for the client, this simply shuts down the client instantly as there is nothing they can do without the server.
<br>

2. *ForcedExit*: Exit gracefully if user attempts to manually kill the program (e.g. CTRL + C) by ensuring they get logged out before shutting down. 
<br>

**Test Suite Ideas**
1. Run the server separately, and have a testing file that simulates one or more users interacting with the server
2. Test via what output the client and/or server receives.
3. Or test via querying the database to check operations were performed correctly.

## Ledger

#### April 6th

* Day 1 of work on this was mostly a disaster. We decided to work from our `gRPC` code as we felt it was significantly cleaner. However, I attempted to bite this off all in one go, severely underestimating how much actually needed changing. This disaster can be seen in `GRPC-Simple`, which should be renamed to `bin` or `trash` or something. I attempted to create a new `Server` object outside of our `ClientHandler`, which just made things needlessly more complicated. In future I'll just add methods and attributes to this class.

* I then restarted as I had bitten off too much in one go. I first focused on propogating info methods (again, dumb decision), so that sending to a server would pass information onto other servers. I had this essentially run a recursive implementation, so that it would connect to the current server, run the appropriate method, then make that server act as what I called a `SimulatedUser` object, which then called essentially the same method with the next backup. This was a pain, but made sense in that the client didn't need to know where all the servers were - having just one server connection, the servers would do the lifting of passing on the information and knowing where each other were.

* This had some problems though. One it was pretty complicated, two if the first server crashed catastrophically (such that it didn't give the client even just the IP of a backup to try next), the client is screwed. So, new idea: When the client connects to a server, it pulls ALL BACKUPS that that server is aware of, such that if it completely crashes, it doesn't need the server, it knows where to try next. I also changed the recursive implementation where information propogated in essentially a recursive chain to more of a tree: when the client connects to a server, and for example sends a message, that server receives it, processes it, and once it has processed that, it acts like the base of a tree, connecting to all of its backups individually and passing the information onwards.

* I also actually setup the protocol of all of the servers finding out about the others with a couple of `python` `input`s.

* We also setup the server databases to be numbered by the server's `id`.

#### April 7th

* Today we updated the client commands to actually use our server changes - now the `process_command` function in the client is within a `try... except` clause, such that if the command fails, it attempts to connect to a backup. 

#### April 8th

* Today we actually implemented all of the methods that update other servers using the `ServerWorker` object. Basically any time the database on the server is changed in any way, we instantiate a `ServerWorker` with the backups of the current server, and call a method with it that runs the same command on all of the backups to keep them up to date too.

#### April 9th

* At this point we think we kind of meet the spec, but not totally sure about how things should behave on a total restart.

* As such, we implemented a logical clock system, so that each database also stores its clock time (any time a Server updates its database, it increments the clock).

* This allows us to, on restart, sync all databases. The `restore_data` function runs at the end of the server setup - each server connects to all others and finds the one with the highest clock. They all then delete their own local data, and pull the data from the most up-to-date server (i.e. basically any server that was still running before the last total system shutdown)

* For example, now our system can handle this: 2 servers, a connects to 1, it shuts down. a therefore is reconnected to 2. a sends 'hi' to b. server 2 shutsdown. All the servers are restarted. b then logs in (on server 1). b receives the message 'hi', since when the servers setup, they synced the information, and server 1 pulled from 2 as it had a higher clock. The servers after syncing also sync their clocks appropriately.