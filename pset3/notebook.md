# COMPSCI 262 PSET 3: gRPC Strengthening Engineering Ledger

## Assignment Spec
Take one of the two implementations you created for the first design exercise (the chat application) and re-design it so that the system is both persistent (it can be stopped and re-started without losing messages that were sent during the time it was running) and 2-fault tolerant in the face of crash/failstop failures. In other words, replicate the back end of the implementation, and make the message store persistent.

The replication can be done in multiple processes on the same machine, but you need to show that the replication also works over multiple machines (at least two). That should be part of the demo.

As usual, you will demo the system on Demo Day III (April 10). Part of the assignment is figuring out how you will demo both the new features. As in the past, keep an engineering notebook that details the design and implementation decisions that you make while implementing the system. 


## Design Decisions
For this assignment, our gRPC implementation from pset 1 already is persistent, as it stores all messages not already successfully sent to a given client in a SQL database. This way, if the server crashes at any point, those messages can be successfully sent on a restarted server to the clients of interest. Our first major design choice here comes with our interpretation of the spec of this assignment does not require that we store all successfully sent messages, as these were already recieved by the user and storing them all over time would take up too much space. 

The next part of this assignment was to add replication to make our system 2-fault tolerant, allowing our chat server to stay running if some piece (either a client or a server) were to fail in some way. We also know that the replication will need to work over multiple machines, meaning that if some part failed on one machine, we could bring it back without failure on another. Some ideas for the server:
- instantiating a client will include checking if a server replica on a non-server computer exists. If it doesn't one will be made on the client machine. 
- maintaining a list of server backups in a set order, using the server at the front
- every time the server gets an update of state, the server will send its updates to its backup, which will send to its backup (three backups total)
- if we switch to a backup server, the machine running the backup will create a local backup of itself there.
    - if we switch to a backup server on a new machine, the new server machine will find a new client machine to also create a backup on
- if no backups nor the current server work (ie. network failure for everyone), handle shutdown comfortably for everyone.


## Demo Ideas
To properly demo our new features, we were thinking about doing the following:
- *persistence*: we would run an instance of the server and clients on multiple machines, send some messages that aren't recieved by a client (ie. sent to a logged out client) and throw them all on airplane mode to disrupt the connection to everyone and cause shutdown. Then, bring the entire system back up. Login to client who will recieve the stored messages, and show how they were stored!
- *replication*: get an instance of the machine running with a server and two clients from three total machines. kill the server instance, and show how it switches to the backup on the server machine. Then, kill the connection on the server machine by switching it to airplane mode, show how one of the client machines becomes the new server. Then could also kill the connection on the secondary server machine with airplane mode, and show how the machine with the single client also becomes a server for itself. 