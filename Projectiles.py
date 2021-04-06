import pygame


class Projectile:
    def __init__(self, x, y, facing, width, game_width, speed, damage, shot_by):
        self._x = x
        self.y = y
        self.width = width
        self.height = 4
        self.game_width = game_width
        self.velocity = facing * speed
        self.damage = damage
        self.erased = False
        self.shot_by = shot_by

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if -50 < value < self.game_width + 50:
            self._x = value
        else:
            self.erased = True

    def draw_projectile(self, window):
        pygame.draw.rect(window, (255, 255, 0), (self.x, self.y, self.width, self.height))


