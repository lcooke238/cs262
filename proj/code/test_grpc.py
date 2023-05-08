import client_grpc
import file_pb2
import pytest
import threading
import os

# File path
FILE_PATH = os.path.abspath("../files/")

# TEST_GRPC
#   test suite for client_grpc.py and server_grpc.py;
#   run by running server_grpc.py in a separate tab,
#   and running 'pytest' in the directory that contains this file.
#   best when RESET_DB = True in server_grpc.py


# tests whether client correctly rejects malformed commands
def test_process_command(capsys):
    client = client_grpc.Client()

    # wrong lengths
    client.process_command("\\hel")
    assert "Invalid command:" in capsys.readouterr().out

    client.process_command("\\delet")
    assert "Invalid command:" in capsys.readouterr().out

    # incorrect commands
    client.process_command("\\outlog")
    assert "Invalid command:" in capsys.readouterr().out

    client.process_command("->")
    assert "Invalid command:" in capsys.readouterr().out

    client.process_command("")
    assert "Invalid command:" in capsys.readouterr().out


# tests login and logout functionality
def test_login_logout(monkeypatch, capsys):
    client = client_grpc.Client()

    # log in as patrick, then log out
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    assert "Successfully logged in as user: patrick." in capsys.readouterr().out
    client.attempt_logout()

    # log in as andrew, then quit fully
    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)
    assert "Successfully logged in as user: andrew." in capsys.readouterr().out
    client.attempt_logout()
    client.channel.close()


# tests the help function
def test_help(monkeypatch, capsys):
    client = client_grpc.Client()

    # make sure help prints correctly
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    client.display_command_help()
    assert "lists files you have access to" in capsys.readouterr().out
    client.attempt_logout()
    client.channel.close()


# tests the list function (in effect, tests upload)
def test_list(monkeypatch, capsys):
    client = client_grpc.Client()

    # log in as patrick, ask for list of no files
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()

    stdout = capsys.readouterr().out
    assert "You have no files available." in stdout

    # then create an ad hoc file and event for the observer to catch manually;
    # check to see if modification is successful and list prints it out
    observer = client_grpc.EventWatcher(client.stub, client.user_token)
    test_file_path = FILE_PATH + '/test_list.txt'
    with open(test_file_path, 'w') as f:
        f.write('hi')

    class Event():
        def __init__(self):
            self.src_path = test_file_path
            self.st_mtime = 100
            self.is_directory = False
    event = Event()

    observer.on_modified(event)

    stdout = capsys.readouterr().out
    assert ("Local modification" in stdout
        and "uploaded to server successfully." in stdout)

    client.attempt_list()

    stdout = capsys.readouterr().out
    assert "test_list.txt" in stdout

    client.attempt_logout()
    client.channel.close()


# tests the drop function
def test_drop(monkeypatch, capsys):
    client = client_grpc.Client()

    # log in as patrick, add a file and make sure it's there
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_drop.txt" not in stdout

    observer = client_grpc.EventWatcher(client.stub, client.user_token)
    test_file_path = FILE_PATH + '/test_drop.txt'
    with open(test_file_path, 'w') as f:
        f.write('hi')
    class Event():
        def __init__(self):
            self.src_path = test_file_path
            self.st_mtime = 100
            self.is_directory = False
    event = Event()

    observer.on_modified(event)
    stdout = capsys.readouterr().out
    assert ("Local modification" in stdout
        and "uploaded to server successfully." in stdout)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_drop.txt" in stdout

    # ask to drop file and delete locally, check its gone
    client.attempt_drop("test_drop.txt")
    os.remove(FILE_PATH + "/test_drop.txt")
    stdout = capsys.readouterr().out
    assert "Dropped test_drop.txt successfully." in stdout

    client.attempt_logout()
    client.channel.close()


# tests delete functionality
def test_delete(monkeypatch, capsys):
    client = client_grpc.Client()

    # log in as patrick, add a file and make sure it's there
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_delete.txt" not in stdout

    observer = client_grpc.EventWatcher(client.stub, client.user_token)
    test_file_path = FILE_PATH + '/test_delete.txt'
    with open(test_file_path, 'w') as f:
        f.write('hi')
    class Event():
        def __init__(self):
            self.src_path = test_file_path
            self.st_mtime = 100
            self.is_directory = False
    event = Event()

    observer.on_modified(event)
    stdout = capsys.readouterr().out
    assert ("Local modification" in stdout
        and "uploaded to server successfully." in stdout)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_delete.txt" in stdout

    # logout as patrick; log back in again and make sure file is still there
    client.attempt_logout()
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_delete.txt" in stdout

    # delete as patrick; log back in again to see if file is gone
    client.attempt_delete()
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_delete.txt" not in stdout

    client.attempt_logout()
    client.channel.close()


# tests pulling from server
def test_sync(monkeypatch, capsys):
    client = client_grpc.Client()

    # log in as patrick, add a file and make sure it's there
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_sync.txt" not in stdout

    observer = client_grpc.EventWatcher(client.stub, client.user_token)
    test_file_path = FILE_PATH + '/test_sync.txt'
    with open(test_file_path, 'w') as f:
        f.write('hi')
    class Event():
        def __init__(self):
            self.src_path = test_file_path
            self.st_mtime = 100
            self.is_directory = False
    event = Event()

    observer.on_modified(event)
    stdout = capsys.readouterr().out
    assert ("Local modification" in stdout
        and "uploaded to server successfully." in stdout)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert "test_sync.txt" in stdout

    # log out and change file while logged out
    client.attempt_logout()
    with open(test_file_path, 'a') as f:
        f.write("!")

    # log back in, complete a sync via a timed-out listener thread
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    thread = threading.Thread(target=client.listen, args=(threading.Condition(),))
    thread.daemon = True
    thread.start()
    thread.join(1)

    client.attempt_list()
    stdout = capsys.readouterr().out
    assert f"Successful sync at {test_file_path}" in stdout

    client.attempt_logout()
    client.channel.close()
