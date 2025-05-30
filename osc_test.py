from scope.osc_ps5000a import ScopePS5000a as scope
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Acquisition
NSAMPLES = 16384 # t = 25 * 8 = 200 us
TIMEBASE = 3 # 8 ns
NAVERAGES = 20

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

osc = scope()

osc.configChannelA()
osc.configChannelB(enabled=False)
osc.configTrigger()
cmaxSamples, timeIntervalns = osc.setAcquisition(NSAMPLES, 256, timebase=TIMEBASE) # timebase 3 = 8ns
times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

fig, ax = plt.subplots()
chA, = ax.plot([], [], label='Channel A')
chB, = ax.plot([], [], label='Channel B')
ax.set_ylim(-10000, 10000)
ax.set_xlim(0, times[len(times)-1])

def update(frame):
    osc.runBlockAcquisition(NAVERAGES)
    osc.waitDataReady()
    chA_data = osc.getData(NAVERAGES)#, adc2mVChBMax = osc.getData()
        
    chA_array = np.array(chA_data)
    chA_arrMean = np.mean(chA_array, axis=0)
    chA_avgList = chA_arrMean.tolist()

    chA_filtered = bandpass_filter(chA_avgList, 600000, 1800000, 125000000)

    chA.set_data(times, chA_data[0])

    return chA

update(0)
ani = animation.FuncAnimation(fig, update, frames=range(100), blit=True)
plt.show()

osc.close()