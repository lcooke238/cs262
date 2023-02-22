import client_grpc
import sys

# tests whether client correctly rejects malformed commands
def test_process_command(capsys):
    client = client_grpc.Client()

    # wrong lengths
    client.process_command("\\hel")
    assert "Invalid command: " in capsys.readouterr().out

    client.process_command("\\delet")
    assert "Invalid command:" in capsys.readouterr().out

    # incorrect commands
    client.process_command("\\outlog")
    assert "Invalid command:" in capsys.readouterr().out

    client.process_command("->")
    assert "Invalid command:" in capsys.readouterr().out

    client.process_command("")
    assert "Invalid command:" in capsys.readouterr().out


def test_login(monkeypatch, capsys):
    
    client = client_grpc.Client()
    monkeypatch.setattr('builtins.input', lambda _: "patrick")
    
    client.run(testing=True)
    
    client.attempt_send("hello patrick -> patrick")
    assert(True == False)
    assert "patrick > hello patrick" in capsys.readouterr().out
    client.attempt_logout()
    client.attempt_logout()
