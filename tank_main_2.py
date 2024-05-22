from scope.osc_ps5000a import ScopePS5000a as scope
from  xyz_motor.xyz_ctrl import XyzController
from xyz_motor.path_builder import PathBuilder
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np
import pygame
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import matplotlib
matplotlib.use('Agg')

pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
PLOT_WIDTH = 600
PLOT_HEIGHT = 600

# Set up display
width, height = WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

def draw_figure(canvas, rect):
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba().tobytes()  # Convert memoryview to bytes
    size = canvas.get_width_height()

    # Convert raw_data to a pygame image
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(surf, rect)

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

#initialize oscilloscope
osc = scope()
osc.configChannelA()
osc.configChannelB(0)
osc.configTrigger()
cmaxSamples, timeIntervalns = osc.setAcquisition(4096, 256)
times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

#initialize oscilloscope plot
#fig, ax = plt.subplots(figsize=(PLOT_WIDTH / 100, PLOT_HEIGHT / 100))
#chA, = ax.plot([], [], label='Channel A')
#chB, = ax.plot([], [], label='Channel B')
#ax.set_ylim(-10000, 10000)
#ax.set_xlim(0, times[len(times)-1])

#get actual position in mm
pos_mm = xyz.get_actual_pos_mm(usteps_mm)

def create_osc_plot(t, chA = [], chB = []):
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH / 100, PLOT_HEIGHT / 100))
    ax.plot(t, chA, label='Channel A')
    #ax.plot(t, chB, label='Channel B')
    ax.set_ylim(-10000, 10000)
    ax.set_xlim(0, times[len(times)-1])
    return fig

def create_3d_plot(x, y, z):
    fig = plt.figure(figsize=(PLOT_WIDTH / 100, PLOT_HEIGHT / 100))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the single point
    point = ax.scatter([x], [y], [z], c='r', marker='o')

    # Draw dashed lines to the planes
    ax.plot([x, x], [y, y], [0, z], color='gray', linestyle='--', alpha=0.5)
    ax.plot([x, x], [0, y], [z, z], color='gray', linestyle='--', alpha=0.5)
    ax.plot([0, x], [y, y], [z, z], color='gray', linestyle='--', alpha=0.5)

    max_range = 500

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')
    
    # Flip the axes
    ax.set_xlim(max_range, 0)
    ax.set_ylim(max_range, 0)
    ax.set_zlim(max_range, 0)

    return fig

running = True
frame = 0

start = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_keys()

    # Update position based on velocity
    actx, acty, actz = xyz.get_actual_pos()
    position = [actx, acty, actz]
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
    #print("Position: [" + strx + ", " + stry + ", " + strz + "]")
    
    cmaxSamples = osc.runBlockAcquisition()
    adc2mVChAMax = osc.getData() #, adc2mVChBMax = osc.getData()

    screen.fill((255, 255, 255))

    #start = time.time()
    fig = create_osc_plot(times, adc2mVChAMax)
    #end = time.time()
    #t = end-start
    #print("{:.2f}".format(t))

    canvas = FigureCanvas(fig)
    draw_figure(canvas, (0, 0, PLOT_WIDTH, PLOT_HEIGHT))
    plt.close(fig)


    #start = time.time()
    start = time.time()
    fig3d = create_3d_plot(pos_mm[0], pos_mm[1], pos_mm[2])

    canvas2 = FigureCanvas(fig3d)
    draw_figure(canvas2, (PLOT_WIDTH, 0, PLOT_WIDTH, PLOT_HEIGHT))
    plt.close(fig3d)

    pygame.display.flip()

    end = time.time()
    t = end-start
    start = end
    print("{:.2f}".format(t))
    


osc.close()
pygame.quit()




