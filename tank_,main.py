from scope.osc_ps5000a import ScopePS5000a as scope
from  xyz_motor.xyz_ctrl import XyzController
from xyz_motor.path_builder import PathBuilder
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np
import pygame

import matplotlib
matplotlib.use('Agg')

pygame.init()

# Set up display
width, height = 1024, 1024
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

xyz = XyzController()
xyz.goto_home()
time.sleep(1)
xyz.zero_absolute_pos()
time.sleep(1)

velocity = [0, 0, 0]

usteps_mm = 40 * 256

def handle_keys():
    global velocity
    keys = pygame.key.get_pressed()

    step = 4000
    if keys[pygame.K_LSHIFT]:
        step = 50000
    elif keys[pygame.K_LCTRL]:
        step = 50

    if keys[pygame.K_UP]:
        velocity[0] = step
    elif keys[pygame.K_DOWN]:
        velocity[0] = -step
    else:
        velocity[0] = 0

    if keys[pygame.K_LEFT]:
        velocity[1] = step
    elif keys[pygame.K_RIGHT]:
        velocity[1] = -step
    else:
        velocity[1] = 0

    if keys[pygame.K_a]:
        velocity[2] = -step
    elif keys[pygame.K_z]:
        velocity[2] = step
    else:
        velocity[2] = 0

print("Position XYZ to measurement Z axis center and press ENTER")

osc = scope()
osc.configChannelA()
osc.configChannelB(0)
osc.configTrigger()
cmaxSamples, timeIntervalns = osc.setAcquisition(4096, 256)
times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

fig, ax = plt.subplots(figsize=(width / 100, height / 100))
chA, = ax.plot([], [], label='Channel A')
chB, = ax.plot([], [], label='Channel B')
ax.set_ylim(-10000, 10000)
ax.set_xlim(0, times[len(times)-1])

running = True
frame = 0

pos_mm = xyz.get_actual_pos_mm(usteps_mm)
start = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_keys()

    # Update position based on velocity
    x, y, z = xyz.get_actual_pos()
    position = [x, y, z]
    position[0] += velocity[0]
    position[1] += velocity[1]
    position[2] += velocity[2]
    #xyz.goto_xyz_relative(velocity[0], velocity[1], velocity[2], False)
    xyz.goto_xyz_absolute(position[0], position[1], position[2], False)

    prev_pos = pos_mm
    pos_mm = xyz.get_actual_pos_mm(usteps_mm)
    end = time.time()
    # Print the updated position
    strx = "{:.2f}".format(pos_mm[0])
    stry = "{:.2f}".format(pos_mm[1])
    strz = "{:.2f}".format(pos_mm[2])
    print("Position: [" + strx + ", " + stry + ", " + strz + "]")
    
    cmaxSamples = osc.runBlockAcquisition()
    adc2mVChAMax = osc.getData() #, adc2mVChBMax = osc.getData()
    chA.set_data(times, adc2mVChAMax)
    #chB.set_data(times, adc2mVChBMax)

    # Clear screen
    screen.fill((0, 0, 0))

    # Blit the matplotlib figure onto the pygame screen
    fig.canvas.draw()
    plot_surf = pygame.image.fromstring(fig.canvas.tostring_rgb(), fig.canvas.get_width_height(), "RGB")
    
    screen.blit(plot_surf, (0, 0))

    # Update display
    pygame.display.flip()

    clock.tick(30)

plt.close()
osc.close()





