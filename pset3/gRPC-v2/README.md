## Installation instructions

To be able to run the gRPC version of our chat application you need the following:

* gRPC installed

-> run `python -m pip install grpcio`

* gRPC tools installed

-> run `python -m pip install grpcio-tools`

* sqlite3 installed

-> run `pip install sqlite3`

* pytest installed

-> run `pip install -U pytest`

## Running instructions

We have our server setup to run in two modes: INTERNAL or EXTERNAL. If you'd like to try things locally on one laptop, you can use INTERNAL - this will set the Server to host on 127.0.0.1 so it won't accept external connections. If you'd like to try things with multiple machines, everywhere you run a server, set the mode to EXTERNAL.

Then to run our chat application you need to:

* Connect all laptops to the same WiFi network (if EXTERNAL)
* Start all the servers, giving each a unique id (if they are on the same machine, on different machines can have same id) by running `server_grpc.py` in the code directory. One Server MUST have id = 0.
* Give each server the correct backup information (how many servers are you running in total - 1 is number of backups for each)
* Give each server the IP and port of all other servers.
* Once all servers are configured, hit enter on all servers to sync the data on the servers.
* The servers are now configured and running.
* Now for any client wishing to connect, configure `HOST_IP` to be the IP of the server with `id = 0`.
* Run `client_grpc.py` on all laptops for clients

### Updating protos

Note for our group: to update the protos, run this command from within the code or protos folder to rebuild the protos:

```python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/chat.proto```