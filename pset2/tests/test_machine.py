import sys
sys.path.append('../code')
import machine

# TEST_MACHINE
#   Test suite for machine.py.
#   Run with USE_MANUAL_CLOCK_RATES and USE_MANUAL_STATES = False.
#
#   To get test_sync() to work,
#   run after running the machine for 15+ seconds
#   with the following values for the 'experimental constants';
#
#   MAX_RANDOM_STATE = 10
#   USE_MANUAL_CLOCK_RATES = True
#   manual_clock_rates = {
#               0: 1,
#               1: 2,
#               2: 6,
#           }
#   USE_MANUAL_STATES = True
#   manual_states = {
#               0: [4] * 14 + [1] + [4] * 10000,
#               1: [4] * 14 + [2] + [4] * 10000,
#               2: [4] * 19 + [3] + [4] * 10000,
#           }
#
#   This way, we can check our machine's functionality against a precise
#   series of events among the three machines, so we know exactly what the logs
#   should look like. In this case, we have three machines, where
#
#   MACHINE 0: Clock speed 1; runs all internal events except for its fifteenth
#       event that is not a reception, which will be a send to machine 1
#   MACHINE 1: Clock speed 2; runs all internal events except for its fifteenth
#       event that is not a reception, which will be a send to machine 0
#   MACHINE 2: Clock speed 6; runs all internal events except for its twentieth
#       event that is not a reception, which will be a send to both other machines
#
#   Then there are three events to keep track of; the first thing to occur will be
#   machine 2's double send. This should happen after 4 clock cycles of machine 0
#   (machine 2's twentieth clock cycle happens after 3 and 1/6 seconds, so machine 0
#   will catch it after 3 seconds = after the fourth cycle) and after 7 clock cycles
#   of machine 1 (again, after 3 seconds = after the seventh cycle for machine 1,
#   since we had cycles for each of 0, .5, 1, 1.5, 2, 2.5, and 3 seconds).
#
#   On the next event, since both machines 0 and 1 are slower than machine 2,
#   each machine should report its local clock as 21.
#
#   Next is machine 1's send to machine 0, which happens after 15 non-reception events
#   for machine 1. Since machine 1 had 7 of those events before the send from machine 2,
#   we should see that the send occurs at local clock time 21 plus the 8 other non-reception
#   events machine 1 must undertake; so the send should happen at local clock time 29.
#
#   This send from machine 1 happens on its 16th clock cycle (15 non-receptions plus
#   one reception), which happens after 7 and 1/2 seconds, so machine 0 will catch it after
#   7 seconds = after the 8th machine 0 clock cycle, whereupon its time will change to 30
#   since machine 0 will certainly have a smaller local clock time.
#
#   Finally, machine 0 has a send on its fifteenth non-reception, which should happen
#   on its 17th clock cycle, accounting for the two receptions it's already had. This should
#   be sent after 16 seconds, so machine 1 should receive it after its 32nd clock cycle.
#   This message should not affect machine 1's clock, since machine 1 should have a higher
#   time than machine 0 at this point.
#
#   All in all, we're looking for:
#
#   MACHINE 0:
#       Correct initialization
#       Correct internal event logging
#       Clock cycle 5: received 20 from machine 2, time 21
#       Clock cycle 9: received 29 from machine 1, time 30
#       Clock cycle 17: sent to machine 1, time 38 (time 30 from above plus (17 - 9))
#
#   MACHINE 1:
#       Correct initialization
#       Correct internal event logging
#       Clock cycle 8: received 20 from machine 2, time 21
#       Clock cycle 16: sent to machine 0, time 29
#       Clock cycle 33: received 38 from machine 0, time 46 (time 29 above plus (33 - 16))
#
#   MACHINE 2:
#       Correct initialization
#       Correct internal event logging
#       Clock cycle 20: sent two messages, time 20 


# tests basic initialization using a custom id
def test_init(capsys):
    m = machine.Machine(3)

    # checking various fields of machine
    assert m.id == 3
    assert m.freq in [1, 2, 3, 4, 5, 6]

    # checking log functionality
    with open("../logs/log_3.txt", 'r') as f:
        log = f.read()
        assert "LOG FOR MACHINE 3 WITH CLOCK SPEED" in log

    # checking completion of init
    assert "Machine with id 3" in capsys.readouterr().out


# checks that synchronization works in the example explained above
def test_sync():
    logs = {}
    for i in range(3):
        with open(f"../logs/log_{i}.txt", "r") as f:
            logs[i] = f.readlines()

    # checks for MACHINE 0 as given above
    assert "LOG FOR MACHINE 0 WITH CLOCK SPEED 1\n" == logs[0][0]
    assert "1 - " in logs[0][1] and "Internal event." in logs[0][1]
    assert "21 - " in logs[0][5] and "Received message: 20." in logs[0][5]
    assert "30 - " in logs[0][9] and "Received message: 29." in logs[0][9]
    assert "38 - " in logs[0][17] and "Sent one message to machine 1." in logs[0][17]

    # checks for MACHINE 1 as given above
    assert "LOG FOR MACHINE 1 WITH CLOCK SPEED 2\n" == logs[1][0]
    assert "1 - " in logs[1][1] and "Internal event." in logs[1][1]
    assert "21 - " in logs[1][8] and "Received message: 20." in logs[1][8]
    assert "29 - " in logs[1][16] and "Sent one message to machine 0." in logs[1][16]
    assert "46 - " in logs[1][33] and "Received message: 38." in logs[1][33]

    # checks for MACHINE 2 as given above
    assert "LOG FOR MACHINE 2 WITH CLOCK SPEED 6\n" == logs[2][0]
    assert "1 - " in logs[2][1] and "Internal event." in logs[2][1]
    assert "20 - " in logs[2][20] and "Sent two messages." in logs[2][20]
