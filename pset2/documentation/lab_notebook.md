# COMPSCI 262 Pset 2: Lab Notebook

## Prompt
Examine logs and discuss the size of jumps in the vals for the logical clocks, drift in the vals of the local logical clocks in the different machines (compared to system time), and the impact different timings on such things as gaps in the logical clock vals and length of the msg queue. Include observations and reflections abt the model and the results of running the model.

## Experiment 1: Default
For our first experiment, we ran our mock system with three connected machines for a minute five separate times, keeping the logs from the most interesting of these runs in the ```../logs/experiment_1``` folder. Our clock randomization was in the default 1-6 range and our machine action randomization was also in the default 1-10 range. Here is what we found:

- **General Observations**: Here, we see that the faster the machine, the longer the log as it was able to do more things in the same amount of time. We also see that slower machines spend more time recieving messages, as they recieve lots of messages from faster machines and are required to get through them all before they can do anything else. We also notice that the last few lines of each log are nonsensical, as logging does not stop when I am in the middle of shutting down the machines. Therefore, I am ignoring the last few lines of each logfile in the rest of my analysis to analyze the system behavior on its own.
- **Jump Size**: The jump sizes between logical clock values were pretty consistent across the board. In increasing speed order, the machine with clock speed 1 had an average jump of 3.849, a min jump of 1, and a max jump of 18; the machine with clock speed 3 had an average jump of 1.968, a min jump of 1, and a max jump of 11; and the machine with clock speed 6 had an average jump of 1, a min jump of 1, and a max jump of 1. As a result, we see that generally as speed increases, the average jump size decreases because less can occur between operations for a faster machine. 
- **Value Drift**: I saw a similar trend with respect to value drift, where the fastest machine had an extremely consistent dif between logical clock and system time around 0.830, the mid-speed machine with an average dif around 1.631, and the slowest machine with a dif around 2.845. The max drift values corresponded quite well with the max jump values from the previous point as well, with the fastest machine sitting right around its average at 0.833, the mid-speed machine sitting at 10.665, and the slowest machine at 17. As a result, we see that generally as speed increases, like with jump size, value drift also decreases because less can occur between logical time steps. 
- **length of message queue**: Here, we see a drastic difference in message queue length between the different machines. The fast and mid-speed machines were relatively comprable, with the fastest machine always having a 0 length queue after removing a message, the mid-spped machine mostly having a 0 length queue with the occasional 1-length from two messages being sent between the same step. However, the slowest machine never had a chance to send messages, as it would get overwhelmed with messages from the faster machines and they would back up in its queue, leading to queue lengths as high as 43. 


## Experiment 2: identical clock cycles
For this experiment, we ran our mock system with three connected machines for a minute five separate times. Our machine randomization remained the same (between 1 and 10), however our clock randomization ceased to be random, and all machines ran with the same speed of 2. Here is what we found:

1. *Jump Size*: 
2. *Value Drift and Explanation*: 
3. *Impact of message queue length*: 

## Experiment 3: No internal events
For this experiment, we ran our mock system with three connected machines for a minute five separate times. Our clock randomization was the default 1-6 range, however, we removed the possibility of an internal event occuring. Here is what we found:

1. *Jump Size*: 
2. *Value Drift and Explanation*: 
3. *Impact of message queue length*: 


## Takeaways
Overall, the logical clock model has been quite useful tool for tracking the order of events in a distributed system, allowing us to order events properly without knowing the exact time that they occured on the system. We saw that the size of jumps in the logical clock values can vary depending on the frequency and timing of events, and that the length of the message queue can also vary depending on the frequency and timing of events. We also thought a bit about the limitations of this simulation in understanding network behavior, ignoring things like network latency, message loss, and machine failures that could all impact the ordering of events.