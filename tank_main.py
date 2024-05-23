
from scope.osc_ps5000a import ScopePS5000a as scope
from xyz_motor.xyz_ctrl import XyzController
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
import tkinter as tk
from tkinter import filedialog
import sys

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
NAVERAGES = 32

# XYZ
USTEPS_MM = 40 * 256

def load_prototxt_file():
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog and return the selected file path
    file_path = filedialog.askopenfilename(
        title="Select measurement config .prototxt file",
        filetypes=(("Prototxt files", "*.prototxt"), ("All files", "*.*"))
    )

    # Check if a file was selected
    if file_path:
        try:
            # Read the content of the file
            with open(file_path, 'r') as file:
                content = file.readlines()
                # Parse the parameters
                params = {}
                for line in content:
                    key, value = line.strip().split(': ')
                    params[key] = float(value)

                xp = params.get('x_pos_range')
                xn = params.get('x_neg_range')

                yp = params.get('y_pos_range')
                yn = params.get('y_neg_range')

                zp = params.get('z_pos_range')
                zn = params.get('z_neg_range')

                xs = params.get('x_step')
                ys = params.get('y_step')
                zs = params.get('z_step')

                return xn, yn, zn, xp, yp, zp, xs, ys, zs
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("No file selected")



def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

def scope_plot(fig_queue, stop_event, osc):
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
            adc2mVChAMax = osc.getData()#, adc2mVChBMax = osc.getData()

            adc2mVChAMax_filt = bandpass_filter(adc2mVChAMax, 600000, 1800000, 125000000)
            
            list_set_A.append(adc2mVChAMax_filt)
            #list_set_B.append(adc2mVChBMax)
            
        chA_array = np.array(list_set_A)
        average_list_A = np.mean(chA_array, axis=0)
        averageA = average_list_A.tolist()

        chA.set_data(times, averageA)
        #chA.set_data(times, [x/1000 for x in adc2mVChBMax])

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()

        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")

        if fig_queue.empty():
            fig_queue.put(surf)

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


pygame.init()

# Set up display
width, height = WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('XYZ tank')

# Initialize XYZ motor controller
xyz = XyzController()
pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)

# Reset xYZ position?
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

if home:
    xyz.goto_home()
    time.sleep(1)
    xyz.zero_absolute_pos()
    time.sleep(1)

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

# Show instructions
instructions = [
    "Use the keyboard to adjust start position:",
    "Up/Down Arrows - Move X-axis ",
    "Left/Right Arrow - Move Y-axis",
    "A/Z Keys - Move Z-axis",
    " ",
    "Press ENTER to continue"
]

instruction_surfaces = [font.render(text, True, (255, 255, 255)) for text in instructions]
instruction_rects = [surface.get_rect(center=(WINDOW_WIDTH/2, (WINDOW_HEIGHT/2) - 72 + (i*36))) for i, surface in enumerate(instruction_surfaces)]

screen.fill((0, 0, 0))

for surface, rect in zip(instruction_surfaces, instruction_rects):
    screen.blit(surface, rect)

waiting_for_input = True
while waiting_for_input:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            try:
                sys.exit("Aborting the script.")
            except SystemExit as e:
                print(f"Script terminated with message: {e}")
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                waiting_for_input = False

        pygame.display.flip()

osc = scope()

# Prepare thread queues
fig_queue = queue.Queue()  # Queue for passing data between threads
stop_event = threading.Event()
scope_thread = threading.Thread(target=scope_plot, args=(fig_queue, stop_event, osc))
scope_thread.daemon = True  # Daemonize the thread so it will exit when the main thread exits
scope_thread.start()  # Start the data generation thread

fig3d_queue = queue.Queue()  # Queue for passing data between threads
position_queue = queue.Queue()
pos3d_thread = threading.Thread(target=xyz_plot3d, args=(fig3d_queue, position_queue,))
pos3d_thread.daemon = True  # Daemonize the thread so it will exit when the main thread exits
#pos3d_thread.start()  # Start the data generation thread

positioning = True
frame = 0

pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
start = time.time()

str_fps = ""

while positioning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            positioning = False
            stop_event.set()
            try:
                sys.exit("Aborting the script.")
            except SystemExit as e:
                print(f"Script terminated with message: {e}")
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                positioning = False

    handle_keys()

    start = time.time()

    if (velocity[0] != 0) or (velocity[1] != 0) or (velocity[2] != 0) :
        # Update position based on velocity
        x, y, z = xyz.get_actual_pos()
        position = [x, y, z]
        position[0] += velocity[0]
        position[1] += velocity[1]
        position[2] += velocity[2]
        #xyz.goto_xyz_relative(velocity[0], velocity[1], velocity[2], False)
        xyz.goto_xyz_absolute(position[0], position[1], position[2], False)
        pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)

    str_pos = "Position [mm]: [" + "{:.2f}".format(pos_mm[0]) + ", " + "{:.2f}".format(pos_mm[1]) + ", " + "{:.2f}".format(pos_mm[2]) + "]"

    if not fig_queue.empty():
        screen.fill((0, 0, 0))
        fig = fig_queue.get()
        screen.blit(fig, (0, 0))
        pygame.display.flip()

    end = time.time()
    t = end - start
    start = end
    if t != 0:
        str_fps = "FPS: " + "{:.2f}".format(1/t)

    window_name = "'XYZ tank, " + str_pos + ", " + str_fps
    pygame.display.set_caption(window_name)

    clock.tick(60)

stop_event.set()
# end scope view thread
time.sleep(1)
scope_thread.join()

def acq_data(fig_queue, stop_event, xyz, osc):

    # Determine measurement path
    posx, posy, posz = xyz.get_actual_pos_mm(USTEPS_MM)
    xn, yn, zn, xp, yp, zp, xs, ys, zs = load_prototxt_file()
    pb = PathBuilder(-xn, -yn, -zn, xp, yp, zp, xs, ys, zs)
    path = pb.generate_path()

    print(path)

    steps = len(path)

    # Convert path from mm to steps
    x = [int(USTEPS_MM * (t[0] + posx)) for t in path]
    y = [int(USTEPS_MM * (t[1] + posy)) for t in path]
    z = [int(USTEPS_MM * (t[2] + posz)) for t in path]

    pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
    str_pos = "Position [mm]: [" + "{:.2f}".format(pos_mm[0]) + ", " + "{:.2f}".format(pos_mm[1]) + ", " + "{:.2f}".format(pos_mm[2]) + "]"

    print(str_pos)

    print("Moving to start position " + str(x[0]) + " " + str(y[0]) + " " + str(z[0]))
    xyz.goto_xyz_absolute(x[0], y[0], z[0], True)

    print("Starting scan")

    n = 0

    #osc = scope()

    str_pos = ""
    str_time = ""

    waveforms = []
    positions = []

    while not stop_event.is_set():
        start = time.time()

        for i in path:
        #start = time.time()
            if stop_event.is_set():
                return
            
            xyz.goto_xyz_absolute(x[n], y[n], z[n], True)
            pos_mm = xyz.get_actual_pos_mm(USTEPS_MM)
            str_pos = "Position " + str(n+1) +"/" + str(steps) + " [mm]: [" + "{:.2f}".format(pos_mm[0]) + ", " + "{:.2f}".format(pos_mm[1]) + ", " + "{:.2f}".format(pos_mm[2]) + "]"
            #print(str_pos)
            
            if n > 1:
                elapsed = time.time() - start
                elapsed_h, remainder = divmod(elapsed, 3600)
                elapsed_m, elapsed_s = divmod(remainder, 60)

                end = (steps-n) * (elapsed/n)
                end_h, remainder = divmod(end, 3600)
                end_m, end_s = divmod(remainder, 60)

                elapsed_str = []
                if elapsed_h > 0:
                    elapsed_str.append("{}h".format(int(elapsed_h)))
                    elapsed_str.append("{}m".format(int(elapsed_m)))
                else:
                    elapsed_str.append("{}m".format(int(elapsed_m)))
                    elapsed_str.append("{}s".format(int(elapsed_s)))

                end_str = []
                if end_h > 0:
                    end_str.append("{}h".format(int(end_h)))
                    end_str.append("{}m".format(int(end_m)))
                else:
                    end_str.append("{}m".format(int(end_m)))
                    end_str.append("{}s".format(int(end_s)))

                str_time = "Elapsed time: " + " ".join(elapsed_str) + ", estimated end in: " + " ".join(end_str)
                #print(str_time)
        
            #time.sleep(0.1)

            t_start = time.time()
            list_set_A = []
            list_set_B = []
            for _ in range(NAVERAGES):
                osc.runBlockAcquisition()
                adc2mVChAMax = osc.getData()#, adc2mVChBMax = osc.getData()

                adc2mVChAMax_filt = bandpass_filter(adc2mVChAMax, 600000, 1800000, 125000000)
                
                list_set_A.append(adc2mVChAMax_filt)
                #list_set_B.append(adc2mVChBMax)
                
            chA_array = np.array(list_set_A)
            average_list_A = np.mean(chA_array, axis=0)
            averageA = average_list_A.tolist()

            t_end = time.time()
            t = t_end - t_start
            print("{:.2f}".format(t))

            position = path[n]

            waveforms.append(averageA)
            positions.append(position)

            data = averageA, str_time, str_pos

            if fig_queue.empty():
                fig_queue.put(data)

            n = n + 1
        
        np.savez("data.npz", waveforms=waveforms, positions=positions)
        return

measuring = True
str_time = ""

# Prepare thread queues
with fig_queue.mutex:
    fig_queue.queue.clear()

print("Starting measurement")

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
ax.set_xlabel('Time [ns]xxx')
ax.set_ylabel('Amplitude [V, mV]')
fig.tight_layout()

stop_event2 = threading.Event()
acq_thread = threading.Thread(target=acq_data, args=(fig_queue, stop_event2, xyz, osc))
acq_thread.daemon = True  # Daemonize the thread so it will exit when the main thread exits
acq_thread.start()  # Start the data generation thread

while measuring:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            measuring = False
            stop_event2.set()
            try:
                sys.exit("Aborting the script.")
            except SystemExit as e:
                print(f"Script terminated with message: {e}")

    if not fig_queue.empty():
        data = fig_queue.get()
        sig = data[0]
        str_time = data[1]
        str_pos = data[2]

        #chB.set_data(times, sig)
        chA.set_data(times, sig)# [x/1000 for x in adc2mVChBMax])

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()

        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")

        window_name = "XYZ tank, " + str_pos + ", " + str_time
        pygame.display.set_caption(window_name)        

        screen.fill((0, 0, 0))
        screen.blit(surf, (0, 0))
        pygame.display.flip()

time.sleep(1)
stop_event2.set()
#xyz.goto_xyz_absolute(10 * usteps_mm, 10 * usteps_mm, 10 * usteps_mm)

print("Scan done")
#xyz.goto_home()

acq_thread.join()
osc.close()
pygame.quit()

