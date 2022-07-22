'''
    Adaptation for AOs
    
    DAQmx Multidevice Synchronization by Sharing a Sample Clock
    https://forums.ni.com/t5/Example-Code/DAQmx-Multidevice-Synchronization-by-Sharing-a-Sample-Clock/ta-p/4101266

    Generates synchronized data from /Dev1/ao0 and /Dev3/ao0
'''

import nidaqmx
import numpy as np
import random
import matplotlib.pyplot as plt

rate = 1000
samples = 1000

# Master task on Dev1
mtask = nidaqmx.Task()
mtask.ao_channels.add_ao_voltage_chan("/Dev1/ao0")
mtask.timing.cfg_samp_clk_timing(
    rate=rate,
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# mtask.timing.ref_clk_src = "OnboardClock"
# mtask.timing.ref_clk_rate = rate



# Slave task on Dev3
stask = nidaqmx.Task()
stask.ao_channels.add_ao_voltage_chan("/Dev3/ao0")
stask.timing.cfg_samp_clk_timing(
    rate=rate,
    source="/Dev1/ao/SampleClock",
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# stask.timing.ref_clk_src = mtask.timing.ref_clk_src
# stask.timing.ref_clk_rate = mtask.timing.ref_clk_rate
stask.triggers.start_trigger.cfg_dig_edge_start_trig(
    trigger_source="/Dev1/ao/StartTrigger"
)


values = np.array(
    [random.uniform(-0.2, 0.2) for _ in range(samples)],
    dtype=np.float64,
)



# Plot written data
fig, ax = plt.subplots()
plt.title('Analog Inputs')
t = np.linspace(0, samples-1, samples)/rate

ax.plot(t, values, linewidth=2)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')

plt.show()


# Start slave first then master
stask.start()
mtask.start()

stask.write(
    values,
    timeout=5,
)
mtask.write(
    values,
    timeout=5,
)


stask.wait_until_done()
mtask.wait_until_done()


# Stop and cleanup
stask.stop()
mtask.stop()

stask.close()
mtask.close()