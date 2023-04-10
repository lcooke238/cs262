(
	trap 'kill 0' SIGINT
	zsh server.sh >/dev/null &
	zsh server2.sh >/dev/null &
	python3 client_grpc.py
)