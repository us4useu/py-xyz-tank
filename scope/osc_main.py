
import numpy as np
import matplotlib.pyplot as plt
from osc_ps5000a import ScopePS5000a as scope
import matplotlib.animation as animation
from scipy.signal import butter, filtfilt
import time
import faulthandler

faulthandler.enable()

NAVERAGES = 20
NSAMPLES = 16384

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

osc = scope()
osc.configChannelA()
osc.configChannelB(0)
osc.configTrigger()
cmaxSamples, timeIntervalns = osc.setAcquisition(NSAMPLES, 256, timebase=3)
times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

fig, ax = plt.subplots()
chA, = ax.plot([], [], label='Channel A')
chB, = ax.plot([], [], label='Channel B')
ax.set_ylim(-2, 2)
ax.set_xlim(0, times[len(times)-1])

def update(frame):
    tstart = time.time()
    osc.runBlockAcquisition(NAVERAGES)
    osc.waitDataReady()
    chA_data = osc.getData(NAVERAGES)#, adc2mVChBMax = osc.getData()

    chA_array = np.array(chA_data)
    chA_arrMean = np.mean(chA_array, axis=0)
    chA_avgList = chA_arrMean.tolist()

    chA_filtered = bandpass_filter(chA_avgList, 600000, 1800000, 125000000)

    chA.set_data(times, chA_filtered)
    #chB.set_data(times, adc2mVChBMax)
    tend = time.time()

    print(tend-tstart)

    return chA, chB

update(0)
ani = animation.FuncAnimation(fig, update, frames=range(100), blit=True)
plt.show()

osc.close()

