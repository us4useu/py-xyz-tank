from xyz_ctrl import XyzController
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 800))

xyz = XyzController()
x, y, z = xyz.get_actual_pos()
position = [x, y, z]
velocity = [0, 0, 0]

usteps_mm = 40 * 256

def handle_keys():
    global velocity
    keys = pygame.key.get_pressed()

    step = 1000
    if keys[pygame.K_LSHIFT]:
        step = 4000
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_keys()

    # Update position based on velocity
    position[0] += velocity[0]
    position[1] += velocity[1]
    position[2] += velocity[2]

    pos_mm = xyz.get_actual_pos_mm(usteps_mm)
    # Print the updated position
    strx = "{:.2f}".format(pos_mm[0])
    stry = "{:.2f}".format(pos_mm[1])
    strz = "{:.2f}".format(pos_mm[2])
    print("Position: [" + strx + ", " + stry + ", " + strz + "]")
    xyz.goto_xyz_absolute(position[0], position[1], position[2], False)

    pygame.time.Clock().tick(30)





