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

pb = PathBuilder(50, 50, 50, 150, 150, 150, 10, 10, 10)
path = pb.generate_path()
for i in path :
    print(i)

x = [int(usteps_mm * t[0]) for t in path]
y = [int(usteps_mm * t[1]) for t in path]
z = [int(usteps_mm * t[2]) for t in path]

xyz = XyzController()
xyz.goto_home()
time.sleep(1)
xyz.zero_absolute_pos()
time.sleep(1)
print("Zero position aftert reset home: " + str(xyz.get_actual_pos()))

n = 0

for i in path :
    xyz.goto_xyz_absolute(x[n], y[n], z[n])
    print("Position " + str(n) + ": " + str(xyz.get_actual_pos()))
    n = n + 1
    time.sleep(0.1)

time.sleep(4)
xyz.goto_xyz_absolute(10 * usteps_mm, 10 * usteps_mm, 10 * usteps_mm)