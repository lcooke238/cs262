import client_grpc
import chat_pb2
import pytest

SUCCESS_WITH_DATA = 2

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
    assert "Successfully logged in as user: patrick. Unread messages:" in capsys.readouterr().out
    client.attempt_logout()

    # log in as andrew, then quit fully
    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)
    assert "Successfully logged in as user: andrew. Unread messages:" in capsys.readouterr().out
    client.attempt_logout()
    client.channel.close()


# tests the help function
def test_help(monkeypatch, capsys):
    client = client_grpc.Client()

    # make sure help prints correctly
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    client.display_command_help()
    assert "match the SQL wildcard provided" in capsys.readouterr().out
    client.attempt_logout()
    client.channel.close()


# tests the list function
def test_list(monkeypatch, capsys):
    client = client_grpc.Client()

    # create user list of patrick, andrew, lauren;
    # then use different wildcards and check output
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    client.attempt_logout()

    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)
    client.attempt_logout()

    monkeypatch.setattr('builtins.input', lambda _: "lauren")
    client.run(testing=True)
    assert "lauren" in capsys.readouterr().out

    client.attempt_list("%")
    stdout = capsys.readouterr().out
    assert ("patrick" in stdout
            and "andrew" in stdout
            and "lauren" in stdout)

    client.attempt_list("%e%")
    stdout = capsys.readouterr().out
    assert ("patrick" not in stdout
            and "andrew" in stdout
            and "lauren" in stdout)

    client.attempt_list("andrew")
    stdout = capsys.readouterr().out
    assert ("patrick" not in stdout
            and "andrew" in stdout
            and "lauren" not in stdout)

    client.attempt_logout()
    client.channel.close()


# tests delete functionality
def test_delete(monkeypatch, capsys):
    client = client_grpc.Client()

    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    client.attempt_logout()

    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)
    client.attempt_logout()

    monkeypatch.setattr('builtins.input', lambda _: "lauren")
    client.run(testing=True)
    assert "lauren" in capsys.readouterr().out

    client.attempt_list("%")
    stdout = capsys.readouterr().out
    assert ("patrick" in stdout
            and "andrew" in stdout
            and "lauren" in stdout)

    # delete lauren; check to see she's gone
    client.attempt_delete()

    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)

    client.attempt_list("%")
    stdout = capsys.readouterr().out
    assert ("patrick" in stdout
            and "andrew" in stdout
            and "lauren" not in stdout)

    # delete andrew; check to see he's gone
    client.attempt_delete()

    monkeypatch.setattr('builtins.input', lambda _: "billy")
    client.run(testing=True)

    client.attempt_list("%")
    stdout = capsys.readouterr().out
    assert ("patrick" in stdout
            and "andrew" not in stdout
            and "lauren" not in stdout
            and "billy" in stdout)

    client.attempt_logout()
    client.channel.close()


def test_send(monkeypatch, capsys):
    client = client_grpc.Client()

    # create user list of patrick, andrew;
    # send 'hi' from andrew to patrick
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)
    client.attempt_logout()

    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client.run(testing=True)
    client.attempt_send("hi -> patrick")
    client.attempt_logout()
    assert "andrew" in capsys.readouterr().out

    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    client.run(testing=True)

    # using relevant code from listen(), outside of the forever-while loop
    response = client.stub.GetMessages(chat_pb2.GetRequest(user=client.user_token))
    if response.status == SUCCESS_WITH_DATA:
        for message in response.message:
            print(f"{message.sender} > {message.message}")
        print(f"{client.user_token} > ", end="")
    assert "hi" in capsys.readouterr().out

    # more legit scenario; patrick and andrew both logged in at once on different clients
    client2 = client_grpc.Client()

    monkeypatch.setattr('builtins.input', lambda _: "andrew")
    client2.run(testing=True)
    client2.attempt_send("hi -> patrick")
    assert "andrew" in capsys.readouterr().out

    response = client.stub.GetMessages(chat_pb2.GetRequest(user=client.user_token))
    if response.status == SUCCESS_WITH_DATA:
        for message in response.message:
            print(f"{message.sender} > {message.message}")
        print(f"{client.user_token} > ", end="")
    assert "hi" in capsys.readouterr().out

    # test a wrong input
    client2.attempt_send("hello")
    assert "Invalid message send syntax" in capsys.readouterr().out

    client.attempt_logout()
    client.channel.close()

    client2.attempt_logout()
    client2.channel.close()
