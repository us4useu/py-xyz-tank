import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
MAIN_PLOT_WIDTH = 1200
MAIN_PLOT_HEIGHT = 800
SIDE_PLOT_WIDTH = 400
SIDE_PLOT_HEIGHT = 400
SIDE2_PLOT_WIDTH = 400
SIDE2_PLOT_HEIGHT = 400

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame with Matplotlib Example")

def draw_figure(canvas, rect):
    """Draw a matplotlib figure on a pygame surface."""
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba().tobytes()  # Convert memoryview to bytes
    size = canvas.get_width_height()

    # Convert raw_data to a pygame image
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(surf, rect)

def create_plot(data, color, size):
    fig, ax = plt.subplots(figsize=size)
    ax.plot(data, color=color)
    return fig

# Main loop
running = True
start_time = time.time()
data_length = 100
update_interval = 0.1  # seconds

data1 = np.random.rand(data_length)
data2 = np.random.rand(data_length)
data3 = np.random.rand(data_length)

while running:
    current_time = time.time()
    if current_time - start_time >= update_interval:
        # Update data
        data1 = np.append(data1[1:], np.random.rand(1))
        data2 = np.append(data2[1:], np.random.rand(1))
        data3 = np.append(data3[1:], np.random.rand(1))
        start_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw the main plot
    fig1 = create_plot(data1, 'r', (MAIN_PLOT_WIDTH / 100, MAIN_PLOT_HEIGHT / 100))
    canvas1 = FigureCanvas(fig1)
    draw_figure(canvas1, (0, 0, MAIN_PLOT_WIDTH, MAIN_PLOT_HEIGHT))
    plt.close(fig1)

    # Draw the first side plot
    fig2 = create_plot(data2, 'g', (SIDE_PLOT_WIDTH / 100, SIDE_PLOT_HEIGHT / 100))
    canvas2 = FigureCanvas(fig2)
    draw_figure(canvas2, (0, MAIN_PLOT_HEIGHT, SIDE_PLOT_WIDTH, SIDE_PLOT_HEIGHT))
    plt.close(fig2)

    # Draw the second side plot
    fig3 = create_plot(data3, 'b', (SIDE2_PLOT_WIDTH / 100, SIDE2_PLOT_HEIGHT / 100))
    canvas3 = FigureCanvas(fig3)
    draw_figure(canvas3, (SIDE_PLOT_WIDTH, MAIN_PLOT_HEIGHT, SIDE_PLOT_WIDTH, SIDE_PLOT_HEIGHT))
    plt.close(fig3)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
