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
from xyz_ctrl import XyzController

usteps_res = [1, 2, 4, 8, 16, 32, 64, 128, 256]
usteps_set = 8

usteps_mm = 40 * 256

pb = PathBuilder(50, 50, 50, 150, 150, 150, 25, 25, 25)
path = pb.generate_path()
for i in path :
    print(i)

steps = len(path)

print("Total steps = " + str(steps))
print("Microsteps per mm = " + str(usteps_mm))

x = [int(usteps_mm * t[0]) for t in path]
y = [int(usteps_mm * t[1]) for t in path]
z = [int(usteps_mm * t[2]) for t in path]

xyz = XyzController()
xyz.goto_home()
time.sleep(1)
xyz.zero_absolute_pos()
time.sleep(1)
print("Zero position aftert reset home: " + str(xyz.get_actual_pos()))
#xyz.goto_end()

print("Starting scan")
time.sleep(1)

n = 0

for i in path :
    xyz.goto_xyz_absolute(x[n], y[n], z[n])
    print("Position " + str(n+1) +"/" + str(steps) + ": " + str(xyz.get_actual_pos_mm(usteps_mm)))
    n = n + 1
    time.sleep(0.1)
    #acquire data here

time.sleep(1)
#xyz.goto_xyz_absolute(10 * usteps_mm, 10 * usteps_mm, 10 * usteps_mm)

print("Scan ended")
xyz.goto_home()

print("Done")
