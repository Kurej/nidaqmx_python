'''
    Adaptation for synchronized multitasks on multiple devices
    
    DAQmx Multidevice Synchronization by Sharing a Sample Clock
    https://forums.ni.com/t5/Example-Code/DAQmx-Multidevice-Synchronization-by-Sharing-a-Sample-Clock/ta-p/4101266

    Generates synchronized data from /Dev1/ao0 and /Dev3/ao0
'''

import numpy as np
import random
import matplotlib.pyplot as plt

import nidaqmx
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx.stream_readers import AnalogMultiChannelReader, CounterReader



# Set shared values
rate = 1000
samples = 1000

# Store channel names in dictionary
chans = {
    "co": "Dev1/Ctr3",
    "ao": "Dev1/ao0,Dev1/ao1,Dev1/ao2,Dev1/ao3",
    "aom": "Dev3/ao0",
    "ai": "Dev1/ai0,Dev1/ai1,Dev1/ai2,Dev1/ai3",
    "ci": "Dev1/Ctr1"
}



# Create and setup co task
cotask = nidaqmx.Task()
co_chan_names = nidaqmx.utils.unflatten_channel_string(chans["co"])
for chan in co_chan_names:
    cotask.co_channels.add_co_pulse_chan_freq(chan, freq=rate)

# cotask.timing.cfg_samp_clk_timing(
#     rate=rate,
#     sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
#     samps_per_chan=samples,
# )
cotask.timing.cfg_implicit_timing()




# Create and setup ao task
aotask = nidaqmx.Task()
ao_chan_names = nidaqmx.utils.unflatten_channel_string(chans["ao"])
for chan in ao_chan_names:
    aotask.ao_channels.add_ao_voltage_chan(chan)

aotask.timing.cfg_samp_clk_timing(
    rate=rate,
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# aotask.timing.ref_clk_src = "OnboardClock"
# aotask.timing.ref_clk_rate = rate


# Create and setup aom task
aomtask = nidaqmx.Task()
aom_chan_names = nidaqmx.utils.unflatten_channel_string(chans["aom"])
for chan in aom_chan_names:
    aomtask.ao_channels.add_ao_voltage_chan(chan)

aomtask.timing.cfg_samp_clk_timing(
    rate=rate,
    source="/Dev1/ao/SampleClock",
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
aomtask.triggers.start_trigger.cfg_dig_edge_start_trig(
    trigger_source="/Dev1/ao/StartTrigger"
)


# Create and setup ai task
aitask = nidaqmx.Task()
ai_chan_names = nidaqmx.utils.unflatten_channel_string(chans["ai"])
for chan in ai_chan_names:
    aitask.ai_channels.add_ai_voltage_chan(chan)
aitask.timing.cfg_samp_clk_timing(
    rate=rate,
    source="/Dev1/ao/SampleClock",
    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    samps_per_chan=samples,
)
# aitask.timing.ref_clk_src = aotask.timing.ref_clk_src
# aitask.timing.ref_clk_rate = aotask.timing.ref_clk_rate
aitask.triggers.start_trigger.cfg_dig_edge_start_trig(
    trigger_source="/Dev1/ao/StartTrigger"
)



# Generate ao values and preallocate ai values
ao_vals = np.array(
    [random.uniform(-0.2, 0.2) for _ in range(len(ao_chan_names)*samples)],
    dtype=np.float64,
)
ao_vals = np.reshape(ao_vals, (len(ao_chan_names), samples))

aom_vals = np.array(
    [random.uniform(-0.2, 0.2) for _ in range(len(aom_chan_names)*samples)],
    dtype=np.float64,
)
aom_vals = np.reshape(aom_vals, (len(aom_chan_names), samples))

ai_vals = np.zeros((len(ai_chan_names), samples), dtype=np.float64)



# Set writers and readers
ao_writer = AnalogMultiChannelWriter(aotask.out_stream)
aom_writer = AnalogMultiChannelWriter(aomtask.out_stream)
ai_reader = AnalogMultiChannelReader(aitask.in_stream)


# Start tasks
aitask.start()
aotask.start()
aomtask.start()
cotask.start()


# Write/read values
ao_writer.write_many_sample(ao_vals)
aom_writer.write_many_sample(aom_vals)
ai_reader.read_many_sample(
    ai_vals,
    number_of_samples_per_channel=samples,
    )

aitask.wait_until_done()
aomtask.wait_until_done()
aotask.wait_until_done()


# Plot data
fig, ax = plt.subplots()
plt.title('Analog I/O')
t = np.linspace(0, samples-1, samples)/rate

ax.plot(t, ao_vals[0,:], linewidth=2, label='Dev1/ao0')
ax.plot(t, aom_vals[0,:], linewidth=2, label='Dev3/ao0')
ax.plot(t, ai_vals[0,:], linewidth=2, label='Dev1/ai0')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')

plt.legend()
plt.show()



# Stop and cleanup
aitask.stop()
aomtask.stop()
aotask.stop()
cotask.stop()

aitask.close()
aomtask.close()
aotask.close()
cotask.close()
