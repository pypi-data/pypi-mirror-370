import pygame

class ResolutionManager:
    def __init__(self, base_width=1920, base_height=1080, fullscreen=False, windowed_size=(1280, 720)):
        pygame.init()
        self.base_width = base_width
        self.base_height = base_height
        self.fullscreen = fullscreen

        if fullscreen:
            info = pygame.display.Info()
            self.screen_width, self.screen_height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen_width, self.screen_height = windowed_size
            self.screen = pygame.display.set_mode(windowed_size)

        #Scaling factors
        self.scale_x = self.screen_width / self.base_width
        self.scale_y = self.screen_height / self.base_height

    #Return scaled size
    def get_scaled_size(self, width, height):
        return int(width * self.scale_x), int(height * self.scale_y)

    #Return scaled position
    def get_scaled_pos(self, x, y):
        return int(x * self.scale_x), int(y * self.scale_y)

    #Return screen surface
    def get_screen(self):
        return self.screen
