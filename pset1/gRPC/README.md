## Installation instructions

To be able to run the gRPC version of our chat application you need the following:

* gRPC installed

-> run `python -m pip install grpcio`

* gRPC tools installed

-> run `python -m pip install grpcio-tools`

* sqlite3 installed

-> run `pip install sqlite3`

## Running instructions

To run the gRPC version of our chat application you need to:

* Connect all laptops to the same WiFi network.
* Find the IP address of the laptop you wish to be the server
* Set `HOST_IP` within client_grpc.py
* Run `client_grpc.py` on all laptops for clients
* Run `server_grpc.py` on the laptop for the server

### Updating protos

Note for our group: to update the protos, run this command from within the code or protos folder to rebuild the protos:

```python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/chat.proto```