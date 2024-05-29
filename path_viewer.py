from xyz_motor.path_builder import PathBuilder
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import numpy as np 
import tkinter as tk
from tkinter import filedialog

def plot_path(path):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x_vals = [x for x, _, _ in path]
    y_vals = [y for _, y, _ in path]
    z_vals = [z for _, _, z in path]

    ax.plot(x_vals, y_vals, z_vals, color='green', marker='o', linestyle='-')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Path')

    plt.show()

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
            params = {}
            # Read the content of the file
            with open(file_path, 'r') as file:
                 for line in file:
                    line = line.strip()
                    if ':' in line:
                        # Split the line into key and value
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Handle float and string types
                        if value.startswith('"') and value.endswith('"'):
                            params[key] = value.strip('"')
                        else:
                            try:
                                params[key] = float(value)
                            except ValueError:
                                params[key] = value

            # Define the expected parameters
            expected_params = [
                'x_pos_range', 'x_neg_range',
                'y_pos_range', 'y_neg_range',
                'z_pos_range', 'z_neg_range',
                'x_step', 'y_step', 'z_step',
                'axis_priority'
            ]

            try:
                return [params[param] for param in expected_params]
            except KeyError as e:
                raise ValueError(f"Required parameter {e} not found in the prototxt file")
                
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("No file selected")

def animate_path(path, interval):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_vals = [x for x, _, _ in path]
    y_vals = [y for _, y, _ in path]
    z_vals = [z for _, _, z in path]

    # Initial plot
    scat = ax.scatter(x_vals, y_vals, z_vals, color=(1, 1, 1, 0))
    line, = ax.plot([], [], [], color='green')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Path Animation')

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    x_middle = np.mean(x_limits)
    y_middle = np.mean(y_limits)
    z_middle = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    def update(frame):
        # Update the colors of the points
        colors = ['green' if i == frame else (1, 1, 1, 0) for i in range(len(path))]
        scat.set_color(colors)
        line.set_data(x_vals[:frame+1], y_vals[:frame+1])
        line.set_3d_properties(z_vals[:frame+1])
        return scat, line

    ani = animation.FuncAnimation(fig, update, frames=len(path), interval=interval, blit=True)
    plt.show()

xp, xn, yp, yn, zp, zn, xs, ys, zs, prio = load_prototxt_file()

spanX = (-xn, xp)
spanY = (-yn, yp)
spanZ = (-zn, zp)

pb = PathBuilder(spanX, spanY, spanZ, xs, ys, zs, priority=prio, Yup=False)

path = pb.generate_path()
print(len(path))

n = len(path)

if n < 1:
    n = 1

#draw in 10 seconds
interval = int(10000/n)

if interval < 1:
    interval = 1

animate_path(path, interval)
