Instructions for Patrick/Lauren

Run this command from within the code or protos folder to rebuild the protos.
python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/chat.proto