import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCM1276
import can
import time
import sys
from path_builder import PathBuilder
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

pb = PathBuilder(0, 0, 0, 100, 100, 100, 10, 10, 10)
path = pb.generate_path()
for i in path :
    print(i)

x = [t[0] for t in path]
y = [t[1] for t in path]
z = [t[2] for t in path]

# Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, color='b', marker='o')

for i in range(len(path) - 1):
    ax.plot([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]], color='b')

# Customize labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()

cm = ConnectionManager("--interface pcan_tmcl")
can_interface = cm.connect()

# Initialize TMCM modules
axisX = TMCM1276(can_interface, 11)
axisY = TMCM1276(can_interface, 12)
#axisZ = TMCM1276(tmcl_module(cm, 13))

motorX = axisX.motors[0]
motorY = axisY.motors[0]

targetX = 00000
targetY = 00000

velocity = 25000

motorX.move_to(targetX, velocity)
motorY.move_to(targetY, velocity)

actualX = motorX.actual_position
actualY = motorY.actual_position

while targetX != actualX or targetY != actualY :
    actualX = motorX.actual_position
    actualY = motorY.actual_position
    print("X = " + str(actualX) + " ,V = " + str(motorX.actual_velocity))
    print("Y = " + str(actualY) + " ,V = " + str(motorY.actual_velocity))
    time.sleep(0.5)

motorX.stop()
motorY.stop()

cm.disconnect()
