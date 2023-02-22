# TEST_CUSTOM
#   test suite for client_custom.py and server_custom.py;
#   run by running server_custom.py in a separate tab,
#   and running 'pytest' in the directory that contains this file.

#imports
import client_custom as chat_client
import pandas as pd
import threading
import sys
import pytest
import io

#constants
server_host = '127.0.0.1'
server_port = 8080
client_host = "127.0.0.1"
client_port = 8080
socket_list = []
online_clients = {}
Head_Len = 4
wp_version = 0
log_name_s = '../logs/testing/test_server_log.txt'
log_name_c = '../logs/testing/test_client_log.txt'
log_name_t = '../logs/testing/test_log.txt'
empty_data = '../data/testing/test_data_empty.csv'
data = '../data/testing/test_data.csv'
users = '../data/testing/test_users.csv'


#assuming server is running, login and run help
def try_help(monkeypatch, capsys):
    open(log_name_c, 'w').close()
    #setup client
    cSocket, username = chat_client.Start_Client(client_host, client_port, log_name_c)
    #display how to access instructions
    chat_client.Display_Message("type \\help to see instructions. Press Enter to look for buffered returns.", log_name)
    monkeypatch.setattr('builtins.input', lambda _: 'Lauren')
    monkeypatch.setattr('builtins.input', lambda _: '\\help')
    #monkeypatch.setattr('sys.stdin', io.StringIO('\\help'))
    msg = "Welcome to the chat service, "+"Lauren"
    assert msg in capsys.readouterr().out

