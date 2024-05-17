import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
import time

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
    screen.blit(surf, rect)

def create_3d_plot(x, y, z):
    fig = plt.figure(figsize=(MAIN_PLOT_WIDTH / 100, MAIN_PLOT_HEIGHT / 100))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the single point
    ax.scatter([x], [y], [z], c='r', marker='o')

    # Draw transparent planes
    max_range = 1.0
    ax.plot([x, x], [y, y], [0, z], color='gray', linestyle='--', alpha=0.5)
    ax.plot([x, x], [0, y], [z, z], color='gray', linestyle='--', alpha=0.5)
    ax.plot([0, x], [y, y], [z, z], color='gray', linestyle='--', alpha=0.5)

    # Draw transparent planes
    xx, yy = np.meshgrid([0, max_range], [0, max_range])
    ax.plot_surface(xx, yy, np.zeros_like(xx), color='gray', alpha=0.1)
    ax.plot_surface(xx, np.zeros_like(yy), yy, color='gray', alpha=0.1)
    ax.plot_surface(np.zeros_like(xx), xx, yy, color='gray', alpha=0.1)

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')
    ax.set_xlim(0, max_range)
    ax.set_ylim(0, max_range)
    ax.set_zlim(0, max_range)
    return fig

# Main loop
running = True
start_time = time.time()
update_interval = 1  # seconds

# Initial data
x_data = np.random.rand(1)[0]
y_data = np.random.rand(1)[0]
z_data = np.random.rand(1)[0]

while running:
    current_time = time.time()
    if current_time - start_time >= update_interval:
        # Update data
        x_data = np.random.rand(1)[0]
        y_data = np.random.rand(1)[0]
        z_data = np.random.rand(1)[0]
        start_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw the 3D plot
    fig = create_3d_plot(x_data, y_data, z_data)
    canvas = FigureCanvas(fig)
    draw_figure(canvas, (0, 0, MAIN_PLOT_WIDTH, MAIN_PLOT_HEIGHT))
    plt.close(fig)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
