import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import matplotlib
matplotlib.use('Agg')

# Initialize pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Set up matplotlib figure and axis
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)

# Initialize data for the plot
x_data = np.linspace(0, 2*np.pi, 100)
y_data = np.sin(x_data)

# Function to update the plot
def update_plot(frame):
    line.set_data(x_data, y_data)
    return line,

# Start matplotlib animation
ani = FuncAnimation(fig, update_plot, frames=range(100), blit=True)

# Set initial position
x, y = width // 2, height // 2
speed = 5

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed

    print(x,y)
    # Clear screen
    screen.fill((0, 0, 0))

    # Blit the matplotlib figure onto the pygame screen
    plot_surf = pygame.image.fromstring(fig.canvas.tostring_rgb(), fig.canvas.get_width_height(), "RGB")
    screen.blit(plot_surf, (0, 0))

    # Draw a simple object representing the position
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()