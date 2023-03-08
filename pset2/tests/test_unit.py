import sys
sys.path.append('../code')
from machine import Machine, MessageType, MESSAGE_SIZE

'''
Methods that these unit tests won't test, but will be tested by integration tests:
1) Run -> Tested via integration tests
2) Listen -> Tested via integration tests
3) Send -> Tested via integration tests
'''

# Test initialization for errors
def test_init():
    m10 = Machine(10)
    assert m10.id == 10
    assert not m10.log_file.closed
    assert m10.clock == 0
    assert m10.queue.empty()
    assert m10.successful_connections == 0

# Test the logical clock behaves as expected
def test_logical_clock():
    m10 = Machine(10)
    # Check if we receive from a clock that is ahead, we jump ahead to that time.
    CLOCK_AHEAD = 99
    m10.queue.put(int.to_bytes(99, MESSAGE_SIZE))
    m10.make_action()
    assert(m10.clock == CLOCK_AHEAD + 1)
    # Check if we receive something from a clock that is behind, we carry on with our clock
    CLOCK_BEHIND = 50
    m10.queue.put(int.to_bytes(CLOCK_BEHIND, MESSAGE_SIZE))
    m10.make_action()
    assert(m10.clock == CLOCK_AHEAD + 2)

def test_log():
    m10 = Machine(10)

    # Test 0: Check for initialization log

    # Test 1: Attempt to log a received where we get no data (error, should be clock time of sender)
    m10.log(MessageType.RECEIVED)

    # Test 2: Attempt to log a SENT_ONE where we get no data (error, should be id of which we sent to)
    m10.log(MessageType.SENT_ONE)

    # Test 3: Attempt to log a received with some simulated
    RECEIVED_CLOCK = 50
    m10.log(MessageType.RECEIVED, data = RECEIVED_CLOCK)

    # Test 4: Now let's actually put it in the queue as if we received a message and check the log again
    # When make_action removes it and logs (should actually update clock appropriately too and log that correctly)
    m10.queue.put(int.to_bytes(RECEIVED_CLOCK))
    m10.make_action()

    # Test 5: Attempt to log a SENT_ONE with some real data (i.e. an id):
    SENDER_ID = 11
    m10.log(MessageType.SENT_ONE, data = SENDER_ID)

    # Test 6: Attempt to log a SENT_TWO message
    m10.log(MessageType.SENT_TWO)

    # Test 7: Attempt to log a INTERNAL message
    m10.log(MessageType.INTERNAL)

    with open(f"../logs/log_10.txt", "r") as f:
        logs = f.readlines()
        # Checking for initialization 
        assert "LOG FOR MACHINE 10 WITH CLOCK SPEED" in logs[0]
        assert "0 - " in logs[1] and "ERROR, Invalid message type." in logs[1]
        assert "0 - " in logs[2] and "ERROR, Invalid message type." in logs[2]
        assert "0 - " in logs[3] and f"Received message: {RECEIVED_CLOCK}. Queue length: 0." in logs[3]
        assert "51 - " in logs[4] and f"Received message: {RECEIVED_CLOCK}. Queue length: 0." in logs[4]
        assert "51 - " in logs[5] and f"Sent one message to machine {SENDER_ID}." in logs[5]
        assert "51 - " in logs[6] and "Sent two messages." in logs[6]
        assert "51 - " in logs[7] and "Internal event." in logs[7]

def test_make_action():
    m10 = Machine(10)
    # Test 1: Check whether make_action internal event behaves correctly. 
    # Note clock should increment as actually made an action
    m10.make_action(7)

    # Test 2: Check whether make_action behaves correctly with item in queue.
    RECEIVED_CLOCK = 50
    m10.queue.put(int.to_bytes(RECEIVED_CLOCK))
    m10.make_action()

    # Other tests require sends - tested in integration tests!

    with open(f"../logs/log_10.txt", "r") as f:
        logs = f.readlines()
        assert "1 - " in logs[1] and "Internal event." in logs[1]
        assert f"{RECEIVED_CLOCK + 1} - " in logs[2] and f"Received message: {RECEIVED_CLOCK}. Queue length: 0." in logs[2]

def test_init_sockets():
    # Testing with a valid machine and invalid machine
    m0 = Machine(0)
    m0.init_sockets()
    m10 = Machine(10)
    m10.init_sockets()
    assert m10.listen_socket
    assert m0.listen_socket
    # Correct machine can only write to other two
    assert len(m0.write_sockets) == 2
    # Incorrect can write to all 3 (but this is an invalid machine according to our limit of 3)
    assert len(m10.write_sockets) == 3
    assert not(m10.write_sockets.get(m10.id, False))
    assert not(m0.write_sockets.get(m0.id, False))
    # Check we open the correct sockets
    assert m0.listen_socket.getsockname() == ('127.0.0.1', 8000)
    assert m10.listen_socket.getsockname() == ('127.0.0.1', 8010)

def test_shutdown():
    m10 = Machine(10)
    # Run some functionality so sockets and file are definitely open
    m10.init_sockets()
    m10.log(MessageType.INTERNAL)
    # Attempt shutdown
    m10.shutdown(testing=True)
    assert m10.log_file.closed
    # Ensure the socket is properly shutdown (shouldn't let us send!)
    try:
        m10.listen_socket.sendall(1)
        assert False
    except:
        assert True