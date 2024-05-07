
import numpy as np
import matplotlib.pyplot as plt
from osc_ps5000a import ScopePS5000a as scope
from matplotlib.animation import FuncAnimation

osc = scope()
osc.configChannelA()
osc.configChannelB()
osc.configTrigger()
timeIntervalns = osc.setAcquisition()

# Show the plot
plt.show()

for n in range(2):
    print(n)
    cmaxSamples = osc.runBlockAcquisition()
    adc2mVChAMax, adc2mVChBMax = osc.getData()

    # Create time data
    time = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

    print(cmaxSamples)
    print(timeIntervalns)

    # plot data from channel A and B
    plt.plot(time, adc2mVChAMax[:])
    plt.plot(time, adc2mVChBMax[:])
    plt.xlabel('Time (ns)')
    plt.ylabel('Voltage (mV)')
    plt.show()

osc.close()

