import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D

import matplotlib
matplotlib.use('Agg')

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
MAIN_PLOT_WIDTH = 800
MAIN_PLOT_HEIGHT = 800

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("3D Position Plot Example")

def draw_figure(canvas, rect):
    """Draw a matplotlib figure on a pygame surface."""
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba().tobytes()  # Convert memoryview to bytes
    size = canvas.get_width_height()

    # Convert raw_data to a pygame image
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    return surf

def create_3d_plot():
    fig = plt.figure(figsize=(MAIN_PLOT_WIDTH / 100, MAIN_PLOT_HEIGHT / 100))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the single point
    point = ax.scatter([], [], [], c='r', marker='o')

    # Draw dashed lines to the planes
    ax.plot([], [], [], color='gray', linestyle='--', alpha=0.5)
    ax.plot([], [], [], color='gray', linestyle='--', alpha=0.5)
    ax.plot([], [], [], color='gray', linestyle='--', alpha=0.5)

    # Draw transparent planes
    max_range = 500
    xx, yy = np.meshgrid([0, max_range], [0, max_range])
    ax.plot_surface(xx, yy, np.zeros_like(xx), color='gray', alpha=0.1)
    ax.plot_surface(xx, np.zeros_like(yy), yy, color='gray', alpha=0.1)
    ax.plot_surface(np.zeros_like(xx), xx, yy, color='gray', alpha=0.1)

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')
    
    # Flip the axes
    ax.set_xlim(max_range, 0)
    ax.set_ylim(max_range, 0)
    ax.set_zlim(max_range, 0)

    return fig, ax, point

# Pre-create the 3D plot
fig, ax, point = create_3d_plot()

# Initial data
x_data = np.random.rand(100) * 500
y_data = np.random.rand(100) * 500
z_data = np.random.rand(100) * 500

def update(frame):
    """Update function for FuncAnimation."""
    global x_data, y_data, z_data

    # Update data
    x_data = np.random.rand(100) * 500
    y_data = np.random.rand(100) * 500
    z_data = np.random.rand(100) * 500

    # Update the plot
    point._offsets3d = (x_data, y_data, z_data)

    # Redraw the canvas
    canvas = FigureCanvas(fig)
    plot_surf = draw_figure(canvas, (0, 0, MAIN_PLOT_WIDTH, MAIN_PLOT_HEIGHT))
    plt.close(fig)

    return plot_surf

# Main loop
running = True
clock = pygame.time.Clock()
frame = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update animation
    plot_surf = update(frame)

    # Clear the screen
    screen.fill((255, 255, 255))

    # Blit the plot onto the screen
    screen.blit(plot_surf, (0, 0))

    # Update frame
    frame += 1
    if frame >= len(x_data):
        frame = 0

    # Update the display
    pygame.display.flip()
    #clock.tick(30)

# Quit Pygame
pygame.quit()
sys.exit()
