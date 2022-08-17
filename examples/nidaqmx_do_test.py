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
from nidaqmx.stream_writers import AnalogMultiChannelWriter, DigitalSingleChannelWriter
from nidaqmx.stream_readers import AnalogMultiChannelReader, CounterReader



# Set shared values
rate = 1
samples = 5

# Store channel names in dictionary
chans = {
    # "do": "Dev1/PFI1",
    "do" : "Dev1/port0/line0",
    "co": "Dev1/Ctr3",
}



# Create and setup co task
# cotask = nidaqmx.Task("Counter")
# co_chan_names = nidaqmx.utils.unflatten_channel_string(chans["co"])
# for chan in co_chan_names:
#     cotask.co_channels.add_co_pulse_chan_freq(chan, freq=rate)

# cotask.timing.cfg_samp_clk_timing(
#     rate=rate,
#     sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
#     samps_per_chan=samples,
# )
# cotask.timing.cfg_implicit_timing()


# Create and setup shutter task
dotask = nidaqmx.Task("Shutter")
do_chan_names = nidaqmx.utils.unflatten_channel_string(chans["do"])
for chan in do_chan_names:
    dotask.do_channels.add_do_chan(chan, "", nidaqmx.constants.LineGrouping.CHAN_PER_LINE)
# dotask.timing.cfg_implicit_timing()
# dotask.timing.cfg_samp_clk_timing(rate, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=samples)
dotask.timing.cfg_samp_clk_timing(rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)




# Set writers and readers
do_writer = DigitalSingleChannelWriter(dotask.out_stream, auto_start=True)
# dotask.write([True, False, True, False, True], auto_start=False)

# Start tasks
dotask.start()
# cotask.start()


# Write/read values
do_writer.write_one_sample_one_line(True)
# do_writer.write_many_sample_port_byte
# dotask.write(True, auto_start=True)
# dotask.write([True, False, True, False], auto_start=False)
# dotask.wait_until_done()

input('Press any key to exit... ')

# Stop and cleanup
do_writer.write_one_sample_one_line(False)
# dotask.write(False, auto_start=False)

dotask.stop()
# cotask.stop()

dotask.close()
# cotask.close()
