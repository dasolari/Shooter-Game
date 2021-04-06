from abc import ABC, abstractmethod
from Projectiles import Projectile
from threading import Thread
from time import sleep
import pygame


# noinspection PyUnresolvedReferences
class Weapon(ABC):
    @abstractmethod
    def __init__(self, x, y, facing, user=None):
        self.user = user
        self._x = x
        self._y = y
        self._magazine = 30
        self.erased = False
        self.falling = True
        self.new_bullet = True
        self.drop_count = 6
        self.recently_grabbed = True
        self.kickback_thread_running = False
        self.kickback_count = self.kickback_count_max
        self.variation = 0
        self.start_sound = None
        self.loop_sound = None
        self.end_sound = None
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.mixer.init()
        self.grab_sound = pygame.mixer.Sound('Sounds/GunCocking.wav')
        if facing == 'R':
            self.left = False
            self.right = True
        else:
            self.left = True
            self.right = False
        self.hitbox = (self.x, self.y, self.width, self.height)

    @property
    def magazine(self):
        return self._magazine

    @magazine.setter
    def magazine(self, value):
        if value <= 0:
            drop_thread = Thread(target=self.drop, daemon=True)
            drop_thread.start()
        else:
            self._magazine = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not self.user:
            if -20 < value < 1131:
                self.erased = True
            else:
                self._x = value
        else:
            self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not self.user:
            if value >= 675:
                self.erased = True
            else:
                self._y = value
        else:
            self._y = value

    def fire(self):
        if self.user and not self.erased:
            u = self.user
            if len(self.y_adjustment) == 1:
                self.variation = 0
            else:
                if self.variation >= len(self.y_adjustment) - 1:
                    self.variation = 0
                else:
                    self.variation += 1
            y = u.y + self.y_adjustment[self.variation]
            if u.right:
                facing = 1
                x = u.x + u.width + 10
            else:
                facing = -1
                x = u.x - 20
            u.game.bullets_in_screen.append(
                Projectile(x, y, facing, self.projectile_width, u.game_width, self.speed, self.damage, u))
            self.magazine -= 1 if not self.user.infinite_ammo else 0

            if self.__class__.__name__ == 'Minigun':
                if not self.channel.get_busy():
                    self.start_sound.play()
                self.channel.play(self.loop_sound, maxtime=300)
                self.channel.queue(self.end_sound)
            else:
                self.channel.play(self.loop_sound)
            self.kickback_thread()

    def rof(self):
        sleep(self.rate_of_fire)
        self.new_bullet = True

    def recently_grabbed_thread(self):
        self.grab_sound.play()
        sleep(1)
        self.recently_grabbed = False

    def drop(self):
        if self.user:
            self.user.weapon = None
            direction = -1 if self.user.right else 1
            while not self.erased:
                self.x += 10 * direction
                if self.drop_count >= -20:
                    neg = 1
                    if self.drop_count < 0:
                        neg = -1
                    self.y -= int((self.drop_count ** 2) * 0.5 * neg)
                    self.drop_count -= 1
                    sleep(0.03)
                else:
                    break
            self.erased = True

    def kickback_thread(self):
        if not self.kickback_thread_running:
            self.kickback_thread_running = True
            thread = Thread(target=self.kickback, daemon=True)
            thread.start()
        else:
            self.kickback_count = self.kickback_count_max

    def kickback(self):
        while self.kickback_count:
            if self.user.right:
                self.user.x -= self.kickback_count
            else:
                self.user.x += self.kickback_count
            self.kickback_count -= 1
            sleep(0.02)
        self.kickback_count = self.kickback_count_max
        self.kickback_thread_running = False

    def draw_weapon(self, window):
        if self.right:
            window.blit(pygame.image.load(self.R_sprite), (self.x, self.y))
        elif self.left:
            window.blit(pygame.image.load(self.L_sprite), (self.x, self.y))
        self.hitbox = (self.x, self.y, self.width, self.height)
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)


class M16(Weapon):
    def __init__(self, x, y, facing, user=None):
        self.L_sprite = 'Sprites/Weapons/M16L.png'
        self.R_sprite = 'Sprites/Weapons/M16R.png'
        self.width = 60
        self.height = 30
        self.projectile_width = 10
        self.rate_of_fire = 0.15
        self.damage = 50
        self.speed = 17
        self.kickback_count_max = 9
        self.x_adjustment_right = 5
        self.x_adjustment_left = 30
        self.y_adjustment = [23]
        super().__init__(x, y, facing, user)
        self._magazine = 30
        self.channel = pygame.mixer.Channel(1)
        self.loop_sound = pygame.mixer.Sound('Sounds/M16Loop.wav')


class L96(Weapon):
    def __init__(self, x, y, facing, user=None):
        self.L_sprite = 'Sprites/Weapons/L96L.png'
        self.R_sprite = 'Sprites/Weapons/L96R.png'
        self.width = 90
        self.height = 30
        self.projectile_width = 15
        self.rate_of_fire = 0.8
        self.damage = 200
        self.speed = 20
        self.kickback_count_max = 23
        self.x_adjustment_right = 5
        self.x_adjustment_left = 58
        self.y_adjustment = [23]
        super().__init__(x, y, facing, user)
        self._magazine = 5
        self.channel = pygame.mixer.Channel(2)
        self.loop_sound = pygame.mixer.Sound('Sounds/L96Loop.wav')


class Minigun(Weapon):
    def __init__(self, x, y, facing, user=None):
        self.L_sprite = 'Sprites/Weapons/MinigunL.png'
        self.R_sprite = 'Sprites/Weapons/MinigunR.png'
        self.width = 113
        self.height = 34
        self.projectile_width = 8
        self.rate_of_fire = 0.01
        self.damage = 15
        self.speed = 14
        self.kickback_count_max = 9
        self.x_adjustment_right = 5
        self.x_adjustment_left = 90
        self.y_adjustment = [25, 26, 27, 28, 29, 30]
        super().__init__(x, y, facing, user)
        self._magazine = 150
        self.firing_thread = None
        self.channel = pygame.mixer.Channel(3)
        self.start_sound = pygame.mixer.Sound('Sounds/MinigunStart.wav')
        self.loop_sound = pygame.mixer.Sound('Sounds/MinigunLoop.wav')
        self.end_sound = pygame.mixer.Sound('Sounds/MinigunEnd.wav')
