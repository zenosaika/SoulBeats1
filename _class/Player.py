import pygame

class Player:
    def __init__(self, x, y, velocity, color):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.velocity
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.velocity
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.velocity
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.velocity