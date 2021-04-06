from abc import ABC, abstractmethod
from time import sleep
from threading import Thread
import pygame


class PowerUp(ABC):
    @abstractmethod
    def __init__(self, x, y, user=None):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 57
        self.user = user
        self.power_up_used = False
        self.erased = False
        self.hitbox = (self.x, self.y, self.width, self.height)

    def power_up_thread(self):
        # noinspection PyUnresolvedReferences
        thread = Thread(target=self.apply_power_up, daemon=True)
        thread.start()

    def draw_power_up(self, window):
        # noinspection PyUnresolvedReferences
        window.blit(pygame.image.load(self.sprite), (self.x - 23, self.y - 11))
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)


class HealthPowerUp(PowerUp):
    def __init__(self, x, y, user=None):
        super().__init__(x, y, user)
        self.sprite = 'Sprites/PowerUps/HealthPowerUp.png'

    def apply_power_up(self):
        if self.user and not self.power_up_used:
            self.user.hp = self.user.max_hp
            self.power_up_used = True
            self.user = None


class InfiniteAmmoPowerUp(PowerUp):
    def __init__(self, x, y, user=None):
        super().__init__(x, y, user)
        self.sprite = 'Sprites/PowerUps/InfiniteAmmoPowerUp.png'

    def apply_power_up(self):
        if self.user and not self.power_up_used:
            self.user.infinite_ammo = True
            sleep(8)
            self.user.infinite_ammo = False
            self.power_up_used = True
            self.user = None


class ShieldPowerUp(PowerUp):
    def __init__(self, x, y, user=None):
        super().__init__(x, y, user)
        self.sprite = 'Sprites/PowerUps/ShieldPowerUp.png'

    def apply_power_up(self):
        if self.user and not self.power_up_used:
            self.user.shield = True
            sleep(5)
            self.user.shield = False
            self.power_up_used = True
            self.user = None
