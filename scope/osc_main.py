
import numpy as np
import matplotlib.pyplot as plt
from osc_ps5000a import ScopePS5000a as scope
import matplotlib.animation as animation

osc = scope()
osc.configChannelA()
osc.configChannelB(0)
osc.configTrigger()
cmaxSamples, timeIntervalns = osc.setAcquisition(4096, 256)
times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

fig, ax = plt.subplots()
chA, = ax.plot([], [], label='Channel A')
chB, = ax.plot([], [], label='Channel B')
ax.set_ylim(-10000, 10000)
ax.set_xlim(0, times[len(times)-1])

def update(frame):
    cmaxSamples = osc.runBlockAcquisition()
    adc2mVChAMax = osc.getData() #, adc2mVChBMax = osc.getData()
    chA.set_data(times, adc2mVChAMax)
    #chB.set_data(times, adc2mVChBMax)

    return chA, chB

update(0)
ani = animation.FuncAnimation(fig, update, frames=range(100), blit=True)
plt.show()

osc.close()

