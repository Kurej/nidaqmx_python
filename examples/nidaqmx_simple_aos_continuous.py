'''
    Generates a single output voltage from a NI card
'''

from math import pi
import nidaqmx
import numpy as np
import random
import matplotlib.pyplot as plt


def create_task(chans, rate, samples, *args):
    task = nidaqmx.Task()
    chlist = nidaqmx.utils.unflatten_channel_string(chans)
    for chan in chlist:
        task.ao_channels.add_ao_voltage_chan(chan)
    task.timing.cfg_samp_clk_timing(
        rate=rate,
        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        samps_per_chan=samples,
    )
    return task



def create_time(rate, samples):
    t_sample = 1/rate
    t_tot = samples*t_sample
    return np.linspace(0, t_tot, samples)



def create_waveform(rate, samples, amp=1, freq=10, type='constant', phase=0, offset=0):
    type = type.lower()
    t = create_time(rate, samples)

    if type == 'constant' or 'dc':
        wf = amp*np.ones(samples, dtype=np.float64)

    elif type == 'sine' or 'sin':
        wf = amp*np.sin(2*pi*freq*t + phase) + offset

    elif type == 'cosine' or 'cos':
        wf = amp*np.cos(2*pi*freq*t + phase) + offset

    elif type == 'random' or 'uniform':
        wf = np.array([random.uniform(-0.2, 0.2) for _ in range(samples)],
                        dtype=np.float64,
                        )

    elif type == '' or 'zero':
        wf = np.zeros(samples, dtype=np.float64)

    else:
        raise NotImplementedError

    # Convert to a line vector in the case of multiple channels in task
    return wf[:,np.newaxis].T



def show_waveform(t, wf):
    fig, ax = plt.subplots()
    plt.title('Waveform')
    ax.plot(t, wf, linewidth=2)
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')

    plt.show()



if __name__ == '__main__':
    SHOW = True
    rate = 1000 # Sampling rate
    samples = 1000 # Number of samples
    chans = '/Dev3/ao0,/Dev3/ao1' # Physical analog outputs (comma separated)
    amps = [2, 5] # Amplitude of both physical analog outputs

    ## Create time vector and waveform
    t = create_time(rate, samples)
    wf1 = create_waveform(rate, samples, amp=amps[0], type='constant')
    wf2 = create_waveform(rate, samples, amp=amps[1], type='constant')
    wf = np.concatenate((wf1, wf2))

    ## Create zeros for cleanup
    wz1 = create_waveform(rate, samples, type='zero')
    wz2 = create_waveform(rate, samples, type='zero')
    wz = np.concatenate((wz1, wz2))

    ## Display waveforms if needed
    if SHOW: show_waveform(t, wf.T)

    # Start the task
    with create_task(chans, rate, samples) as task:
        task.start()
        task.write(wf, timeout=1)
        input('Press any key to exit... ')
        task.write(wz, timeout=1)
        task.stop()  
