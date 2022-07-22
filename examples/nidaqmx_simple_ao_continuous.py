'''
    Generates a single output voltage from a NI card
'''

from math import pi
import nidaqmx
import numpy as np
import random
import matplotlib.pyplot as plt


def create_task(chan, rate, samples, *args):
    task = nidaqmx.Task()
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
        return amp*np.ones(samples, dtype=np.float64)

    elif type == 'sine' or 'sin':
        return amp*np.sin(2*pi*freq*t + phase) + offset

    elif type == 'cosine' or 'cos':
        return amp*np.cos(2*pi*freq*t + phase) + offset

    elif type == 'random' or 'uniform':
        return np.array([random.uniform(-0.2, 0.2) for _ in range(samples)],
                        dtype=np.float64,
                        )
    else:
        raise NotImplementedError



def show_waveform(t, wf):
    fig, ax = plt.subplots()
    plt.title('Waveform')
    ax.plot(t, wf, linewidth=2)
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')

    plt.show()



if __name__ == "__main__":
    SHOW = False
    loop_time = 0.1
    rate = 1000 # Sampling rate
    samples = 1000 # Number of samples
    chan = "/Dev3/ao0"
    amp = 2

    ## Create time vector and waveform
    t = create_time(rate, samples)
    wf = create_waveform(rate, samples, amp=amp, type='constant')
    if SHOW: show_waveform(t, wf)

    ## Start the task
    with create_task(chan, rate, samples) as task:
        task.start()
        task.write(wf, timeout=1)
        input('Press any key to exit... ')
        task.stop()  
