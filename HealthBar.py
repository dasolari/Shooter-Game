import pygame


class HealthBar:
    def __init__(self, player, game):
        self.x = player.x
        self.y = player.y
        self.player = player
        self.max_health_left = 49
        self.health_left = self.max_health_left
        self.previous_hp = self.player.hp
        game.health_bars_in_screen.append(self)

    def x_in_function_of_hp(self):
        hp = self.player.hp
        if hp == self.player.max_hp:
            self.health_left = self.max_health_left
        if not self.previous_hp == hp:
            self.health_left = (hp * self.health_left) / self.player.max_hp
            self.previous_hp = hp

    def draw_health_bar(self, window):
        pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - 11, 50, 10), 2)
        pygame.draw.rect(window, (0, 250, 0), (self.x - 9, self.y - 10, self.health_left, 9))
