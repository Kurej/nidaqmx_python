import numpy as np
import matplotlib.pyplot as plt
import time


# Set script parameters
np.random.seed(10**7)
loop_pause_seconds = 0
loop_number = 100


# Set acquisition parameters
chans = 2
buffer = 100
plotsize = 30*buffer


# Initialize data
data = np.zeros(shape=(plotsize, chans))
x = np.linspace(start=0, stop=plotsize, num=data.shape[0])


# Initialize plots
plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
plt.title('Counter outputs')
plt.xlabel('t [a.u.]')
plt.ylabel('Counts [cps]')
lines = ax.plot(x, data)


# Run plotting loop
for i in range(loop_number):
    for chan in range(chans):
        newdata = np.random.randn(buffer)
        data[:,chan] = np.append(data[buffer:, chan], newdata)
        lines[chan].set_ydata(data[:,chan])

    plt.ylim(np.min(data), np.max(data))

    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(loop_pause_seconds)
