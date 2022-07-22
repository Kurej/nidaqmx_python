'''
    Conversion from Labview to Python of:
    
    DAQmx Multidevice Synchronization by Sharing a Sample Clock
    https://forums.ni.com/t5/Example-Code/DAQmx-Multidevice-Synchronization-by-Sharing-a-Sample-Clock/ta-p/4101266

    Acquires synchronized data from /Dev1/ai0 and /Dev3/ai0
'''

import nidaqmx
import numpy as np
import random
import matplotlib.pyplot as plt

rate = 1000
samples = 1000



# Master task on Dev1
mtask = nidaqmx.Task()
mtask.ai_channels.add_ai_voltage_chan("/Dev1/ai0")
mtask.timing.cfg_samp_clk_timing(
    rate=rate,
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# mtask.timing.ref_clk_src = "OnboardClock"
# mtask.timing.ref_clk_rate = rate


# Slave task on Dev3
stask = nidaqmx.Task()
stask.ai_channels.add_ai_voltage_chan("/Dev3/ai0")
stask.timing.cfg_samp_clk_timing(
    rate=rate,
    source="/Dev1/ai/SampleClock",
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# stask.timing.ref_clk_src = mtask.timing.ref_clk_src
# stask.timing.ref_clk_rate = mtask.timing.ref_clk_rate
stask.triggers.start_trigger.cfg_dig_edge_start_trig(
    trigger_source="/Dev1/ai/StartTrigger"
)



# Start slave first then master
stask.start()
mtask.start()

a = stask.read(
    number_of_samples_per_channel=samples,
    timeout=5,
)
b = mtask.read(
    number_of_samples_per_channel=samples,
    timeout=5,
)


stask.wait_until_done()
mtask.wait_until_done()


# Print plots
fig, ax = plt.subplots()
plt.title('Analog Inputs')
t = np.linspace(0, samples-1, samples)/rate

ax.plot(t, a, linewidth=2)
ax.plot(t, b, linewidth=2)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')

plt.show()



# Stop and cleanup
stask.stop()
mtask.stop()

stask.close()
mtask.close()
