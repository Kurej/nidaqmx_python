import numpy as np
import matplotlib.pyplot as plt

import nidaqmx
from nidaqmx.stream_readers import CounterReader


# Parameters
buffer_size = 10
acq_frequency = 100
duty_cycle = 0.99
sample_clock = 'Dev1/ctr3'
counterA = 'Dev1/ctr1'
counterB = 'Dev1/ctr2'
input_term_A = '/Dev1/PFI0'
input_term_B = '/Dev1/PFI1'


# Tasks
cotask = nidaqmx.Task("Counter")

cotask.co_channels.add_co_pulse_chan_freq(
    counter = sample_clock, 
    freq = acq_frequency,
    units = nidaqmx.constants.FrequencyUnits.HZ,
    idle_state = nidaqmx.constants.Level.LOW,
)

cotask.timing.cfg_implicit_timing(
    sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS,
)


citask = nidaqmx.Task("PMT")

citask.ci_channels.add_ci_pulse_width_chan(
    counter = counterA,
    units = nidaqmx.constants.TimeUnits.TICKS,
)

citask.timing.cfg_implicit_timing(
    sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS,
)





ci_reader = CounterReader(citask.in_stream)
data_init = np.zeros(buffer_size, dtype = np.uint32)
print('im here')

citask.start()
cotask.start()

fig, ax = plt.subplots()
plt.title('Counter outputs')
plt.xlabel('t [a.u.]')
plt.ylabel('Counts [cps]')
ax.plot(data_init, linewidth = 2)



for i in range(10):
    data = ci_reader.read_many_sample_uint32(
        data = data_init,
        number_of_samples_per_channel = buffer_size,
        timeout = 10,
    )
    data_cps = data*acq_frequency
    ax.update({'ydata': data_cps})

# citask.wait_until_done()

citask.stop()
cotask.stop()

citask.close()
cotask.close()
