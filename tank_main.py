
from scope.osc_ps5000a import ScopePS5000a as scope
from  xyz_motor.xyz_ctrl import XyzController
from xyz_motor.path_builder import PathBuilder
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np
import pygame
from pygame.locals import *
import queue
import matplotlib.backends.backend_agg as agg
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy.signal import butter, filtfilt
import pickle

import matplotlib
matplotlib.use('Agg')

# Constants
# Display
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
PLOT_WIDTH = 1600
PLOT_HEIGHT = 800

# Acquisition
NSAMPLES = 16384
TIMEBASE = 3 #
NAVERAGES = 16

# XYZ
USTEPS_MM = 40 * 256

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y


def draw_figure(canvas, rect):
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba().tobytes()  # Convert memoryview to bytes
    size = canvas.get_width_height()

    # Convert raw_data to a pygame image
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(surf, rect)

def scope_plot(fig_queue, stop_event):
    osc = scope()
    osc.configChannelA()
    osc.configChannelB()
    osc.configTrigger()
    cmaxSamples, timeIntervalns = osc.setAcquisition(32768, 256)
    times = np.linspace(0, (cmaxSamples - 1) * timeIntervalns, cmaxSamples)

    fig, ax = plt.subplots(figsize=(PLOT_WIDTH / 100, PLOT_HEIGHT / 100))
    chA, = ax.plot([], [], label='Channel A')
    chB, = ax.plot([], [], label='Channel B')
    ax.set_ylim(-20, 20)
    ax.set_xlim(0, times[len(times)-1])
    ax.set_xlabel('Time [ns]')
    ax.set_ylabel('Amplitude [v, mV]')
    fig.tight_layout()

    while not stop_event.is_set():

        list_set_A = []
        list_set_B = []
        for _ in range(NAVERAGES):
            cmaxSamples = osc.runBlockAcquisition()
            adc2mVChAMax, adc2mVChBMax = osc.getData()

            adc2mVChAMax_filt = bandpass_filter(adc2mVChAMax, 600000, 1800000, 125000000)
            
            list_set_A.append(adc2mVChAMax_filt)
            #list_set_B.append(adc2mVChBMax)
            
        chA_array = np.array(list_set_A)
        average_list_A = np.mean(chA_array, axis=0)
        averageA = average_list_A.tolist()

        chB.set_data(times, averageA)
        chA.set_data(times, [x/1000 for x in adc2mVChBMax])

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()

        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")

        if fig_queue.empty():
            fig_queue.put(surf)
        
    osc.close()

def xyz_plot3d(fig3d_queue, position_queue):

    while True:
        if not position_queue.empty():
            print("got position data")
            pos = position_queue.get()
            x = pos[0]
            y = pos[1]
            z = pos[2]

            fig = plt.figure(figsize=(PLOT_WIDTH / 100, PLOT_HEIGHT / 100))
            ax = fig.add_subplot(111, projection='3d')

            # Plot the single point
            ax.scatter([x], [y], [z], c='r', marker='o')

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
            if fig3d_queue.empty():
                fig3d_queue.put(fig)
        pass

def check_yn(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print("Enter 'y' or 'n'")

pygame.init()

# Set up display
width, height = WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('XYZ tank')

xyz = XyzController()

pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)

font = pygame.font.Font(None, 36)
text_surface = font.render("Do you want to reset XYZ position? (y/n)", True, (255, 255, 255))
text_rect = text_surface.get_rect(center=(800, 400))

waiting_for_input = True
home = False

while waiting_for_input:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_y:
                text_surface = font.render("Resetting XYZ position", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(800, 400))
                waiting_for_input = False
                home = True
            elif event.key == K_n:
                waiting_for_input = False
                home = False

    screen.fill((0, 0, 0))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

#home = check_yn("Do you want to reset XYZ position? (y/n): ")

if home:
    xyz.goto_home()
    time.sleep(1)
    xyz.zero_absolute_pos()
    time.sleep(1)

pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
strx = "{:.2f}".format(pos_mm[0])
stry = "{:.2f}".format(pos_mm[1])
strz = "{:.2f}".format(pos_mm[2])
print("Position: [" + strx + ", " + stry + ", " + strz + "]")

window_name = "Position [mm]: [" + strx + ", " + stry + ", " + strz + "]"
pygame.display.set_caption(window_name)

velocity = [0, 0, 0]

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

fig_queue = queue.Queue()  # Queue for passing data between threads
stop_event = threading.Event()
scope_thread = threading.Thread(target=scope_plot, args=(fig_queue, stop_event,))
scope_thread.daemon = True  # Daemonize the thread so it will exit when the main thread exits
scope_thread.start()  # Start the data generation thread

fig3d_queue = queue.Queue()  # Queue for passing data between threads
position_queue = queue.Queue()
pos3d_thread = threading.Thread(target=xyz_plot3d, args=(fig3d_queue, position_queue,))
pos3d_thread.daemon = True  # Daemonize the thread so it will exit when the main thread exits
#pos3d_thread.start()  # Start the data generation thread

running = True
frame = 0

pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
start = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            stop_event.set()

    handle_keys()

    start = time.time()

    # Update position based on velocity
    x, y, z = xyz.get_actual_pos()
    position = [x, y, z]
    position[0] += velocity[0]
    position[1] += velocity[1]
    position[2] += velocity[2]
    #xyz.goto_xyz_relative(velocity[0], velocity[1], velocity[2], False)
    xyz.goto_xyz_absolute(position[0], position[1], position[2], False)

    pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
    str_x = "{:.2f}".format(pos_mm[0])
    str_y = "{:.2f}".format(pos_mm[1])
    str_z = "{:.2f}".format(pos_mm[2])
    str_pos = "Position: [" + str_x + ", " + str_y + ", " + str_z + "]"

    if not fig_queue.empty():
        screen.fill((0, 0, 0))
        fig = fig_queue.get()
        screen.blit(fig, (0, 0))
        pygame.display.flip()

    end = time.time()
    t = end - start
    start = end
    str_fps = "FPS: " + "{:.2f}".format(1/t)

    window_name = "'XYZ tank, " + str_pos + ", " + str_fps
    pygame.display.set_caption(window_name)

    clock.tick(60)

scope_thread.join()
pygame.quit()

