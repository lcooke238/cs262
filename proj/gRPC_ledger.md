# CS262 Final project Engineering ledger
## Andrew Holmes, Patrick Thornton, Lauren Cooke

Idea: Distributed file system

Desired features:
* Can save a file and have it stored on the distributed file system (some sort of save/edit detection system)
* Can pull the file 

### Saturday 29th

Today we started laying the groundwork for the project. I spent some time writing code to try to keep track of file changes, only to discover about 2 hours in the package watchdog which seems to do everything I did but better, so I switched to that. Now I have a good way of keeping track of local file modifications, it was time to think about how they interact with the server. A few things/situations we thought about:

* 
