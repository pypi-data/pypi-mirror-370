#
Overview
##
This library provides a ResolutionManager class for Pygame that handles resolution scaling across different screen sizes. It allows you to design your game for a base resolution (e.g. 1920x1080) and automatically scale positions, sizes, and images to fit both fullscreen and windowed modes.

####
Basic Usage
####

from resolution_manager import ResolutionManager
import pygame

pygame.init()

#Create class
res = ResolutionManager(fullscreen=False, windowed_size=(1280, 720))

screen = res.get_screen()
clock = pygame.time.Clock()

#Load and scale image
img = pygame.image.load("__internal__/sp_health_100.png").convert_alpha()
img = pygame.transform.scale(img, res.get_scaled_size(300, 300))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    #Draw centered image
    img_rect = img.get_rect(center=(res.screen_width // 2, res.screen_height // 2))
    screen.blit(img, img_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

