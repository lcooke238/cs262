import sys
sys.path.append('../code')
from machine import Machine, MessageType, MESSAGE_SIZE

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
    m10 = Machine(0)
    # Attempt to log a received where we get no data (error, should be clock time of sender)
    m10.log(MessageType.RECEIVED)
    # Attempt to log a SENT_ONE where we get no data (error, should be id of which we sent to)
    m10.log(MessageType.SENT_ONE)
    # Attempt to log a received with some simulated data
    m10.log(MessageType.RECEIVED, data = 50)
    # Attempt to log a SENT_ONE with some real data (i.e. an id):
    m10.log(MessageType.SENT_ONE, data = 11)

    with open(f"../logs/log_10.txt", "r") as f:
        logs = f.readlines()
        # Checking for initialization 
        assert "LOG FOR MACHINE 10 WITH CLOCK SPEED" in logs[0]