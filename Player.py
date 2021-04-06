from abc import ABC, abstractmethod
from time import sleep
from threading import Thread
from HealthBar import HealthBar
import pygame


class Player(ABC):
    @abstractmethod
    def __init__(self, x, y, width, height, velocity, game_width, game_height, game):
        self.game = game
        self._x = x
        self._y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.game_width = game_width
        self.game_height = game_height
        self.jumping = False
        self.jumped_once = False
        self.jump_count = 10
        self.left = False
        self.right = False
        self.walk_count = 0
        self.standing = True
        self.walk_right = []
        self.walk_left = []
        self.incremental_fall = [10] * 5 + [11] * 6 + [12] * 7 + [13] * 8 + [14] * 9 + [15] * 10
        self.fall_count = 0
        self.lives = 5
        self.max_hp = 300
        self._hp = self.max_hp
        self.fixed_x = False
        self.fixed_y = False
        self.shield = False
        self.infinite_ammo = False
        self.new_bullet = True
        self.weapon = None
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.health_bar = HealthBar(self, self.game)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not -20 < value < self.game_width - self.width:
            self.hp = 0
            if self.weapon:
                self.weapon.erased = True
        else:
            if not self.fixed_x:
                self._x = value
                self.health_bar.x = value
                if self.weapon:
                    if self.right:
                        self.weapon.x = value + self.weapon.x_adjustment_right
                    else:
                        self.weapon.x = value - self.weapon.x_adjustment_left
            else:
                self._x = self._x
                self.health_bar.x = self._x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not -200 < value < self.game_height - self.height:
            self.hp = 0
            if self.weapon:
                self.weapon.erased = True
        else:
            if not self.fixed_y:
                self._y = value
                self.health_bar.y = value
                if self.weapon:
                    self.weapon.y = value + 10
            else:
                self._y = self._y
                self.health_bar.y = self._y

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        if value <= 0 and self.lives:
            self.lives -= 1
            self._hp = 0
            self.game.respawn_player(self)
            if self.weapon:
                self.weapon.erased = True
        elif value <= 0 and not self.lives:
            self._hp = 0
            self.game.endgame = True
        elif value > 0:
            self._hp = value
        self.health_bar.x_in_function_of_hp()

    def player_drawing(self, window):
        if self.walk_count + 1 >= 27:
            self.walk_count = 0

        if not self.standing:
            if self.left:
                window.blit(self.walk_left[self.walk_count // 3], (self.x - 17, self.y - 11))
                self.walk_count += 1
            elif self.right:
                window.blit(self.walk_right[self.walk_count // 3], (self.x - 17, self.y - 11))
                self.walk_count += 1
        else:
            if self.right:
                window.blit(self.walk_right[0], (self.x - 17, self.y - 11))
            else:
                window.blit(self.walk_left[0], (self.x - 17, self.y - 11))
        self.hitbox = (self.x, self.y, self.width, self.height)
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)

    def levitate(self):
        self.fixed_x = True
        self.shield = True
        while self.y <= 40:
            self.y += 1
            sleep(0.1)
        self.fixed_y = True
        sleep(4)
        self.fixed_x = False
        self.fixed_y = False
        self.shield = False

    def initialize_respawn(self, x, y):
        self.x, self.y = x, y
        self.jump_count = 10
        self.walk_count = 0
        self.fall_count = 0
        self.jumping = False
        self.jumped_once = False
        self.left = False
        self.right = False
        self.standing = True
        self.hp = self.max_hp

    def shot(self, bullet):
        if not self.shield:
            self.hp -= bullet.damage

    def grab_weapon(self):
        for weapon in self.game.weapons_in_screen:
            if (self.x + int(self.width / 2)) in range(weapon.x, weapon.x + weapon.width)\
                    and (self.y + int(self.height / 2)) in range(weapon.y, weapon.y + weapon.height):
                if not weapon.user:
                    if not self.weapon:
                        self.weapon = weapon if not weapon.user else None
                        self.weapon.user = self if not weapon.user else None
                        if self.right:
                            weapon.right, weapon.left = True, False
                        else:
                            weapon.right, weapon.left = False, True
                        recently_grabbed_thread = Thread(target=self.weapon.recently_grabbed_thread, daemon=True)
                        recently_grabbed_thread.start()
                        break
                    else:
                        if self.weapon != weapon and not self.weapon.recently_grabbed:
                            drop_thread = Thread(target=self.weapon.drop, daemon=True)
                            drop_thread.start()
                            self.weapon = weapon if not weapon.user else None
                            self.weapon.user = self if not weapon.user else None
                            if self.right:
                                weapon.right, weapon.left = True, False
                            else:
                                weapon.right, weapon.left = False, True
                            recently_grabbed_thread = Thread(target=self.weapon.recently_grabbed_thread, daemon=True)
                            recently_grabbed_thread.start()
                            break


class Ice(Player):
    def __init__(self, x, y, width, height, velocity, game_width, game_height, game):
        super().__init__(x, y, width, height, velocity, game_width, game_height, game)
        self.walk_right = [pygame.image.load('Sprites/Characters/R1.png'),
                           pygame.image.load('Sprites/Characters/R2.png'),
                           pygame.image.load('Sprites/Characters/R3.png'),
                           pygame.image.load('Sprites/Characters/R4.png'),
                           pygame.image.load('Sprites/Characters/R5.png'),
                           pygame.image.load('Sprites/Characters/R6.png'),
                           pygame.image.load('Sprites/Characters/R7.png'),
                           pygame.image.load('Sprites/Characters/R8.png'),
                           pygame.image.load('Sprites/Characters/R9.png')]
        self.walk_left = [pygame.image.load('Sprites/Characters/L1.png'),
                          pygame.image.load('Sprites/Characters/L2.png'),
                          pygame.image.load('Sprites/Characters/L3.png'),
                          pygame.image.load('Sprites/Characters/L4.png'),
                          pygame.image.load('Sprites/Characters/L5.png'),
                          pygame.image.load('Sprites/Characters/L6.png'),
                          pygame.image.load('Sprites/Characters/L7.png'),
                          pygame.image.load('Sprites/Characters/L8.png'),
                          pygame.image.load('Sprites/Characters/L9.png')]

    def player_movement(self, keys):
        if keys[pygame.K_MINUS] and self.weapon:
            if self.weapon.new_bullet:
                self.weapon.fire()
                if self.weapon:
                    self.weapon.new_bullet = False
                    thread = Thread(target=self.weapon.rof, daemon=True)
                    thread.start()
        if keys[pygame.K_PERIOD]:
            self.grab_weapon()
        if keys[pygame.K_DOWN] and self.weapon:
            drop_thread = Thread(target=self.weapon.drop, daemon=True)
            drop_thread.start()
        if keys[pygame.K_LEFT]:
            self.x -= self.velocity
            self.left, self.right, self.standing = True, False, False
            if self.weapon:
                self.weapon.left, self.weapon.right = True, False
        elif keys[pygame.K_RIGHT]:
            self.x += self.velocity
            self.left, self.right, self.standing = False, True, False
            if self.weapon:
                self.weapon.left, self.weapon.right = False, True
        else:
            self.standing, self.walk_count = True, 0
        if not self.jumping and not self.jumped_once:
            if keys[pygame.K_UP]:
                self.jumping = True
        elif self.jumping and not self.jumped_once:
            if self.jump_count >= -10:
                neg = 1
                if self.jump_count <= 0:
                    self.jump_count = 10
                    self.jumping = False
                    self.jumped_once = True
                else:
                    self.y -= int((self.jump_count ** 2) * 0.5 * neg)
                    self.jump_count -= 1
            else:
                self.jump_count = 10
                self.jumping = False


class Fire(Player):
    def __init__(self, x, y, width, height, velocity, game_width, game_height, game):
        super().__init__(x, y, width, height, velocity, game_width, game_height, game)
        self.walk_right = [pygame.image.load('Sprites/Characters/R1.png'),
                           pygame.image.load('Sprites/Characters/R2.png'),
                           pygame.image.load('Sprites/Characters/R3.png'),
                           pygame.image.load('Sprites/Characters/R4.png'),
                           pygame.image.load('Sprites/Characters/R5.png'),
                           pygame.image.load('Sprites/Characters/R6.png'),
                           pygame.image.load('Sprites/Characters/R7.png'),
                           pygame.image.load('Sprites/Characters/R8.png'),
                           pygame.image.load('Sprites/Characters/R9.png')]
        self.walk_left = [pygame.image.load('Sprites/Characters/L1.png'),
                          pygame.image.load('Sprites/Characters/L2.png'),
                          pygame.image.load('Sprites/Characters/L3.png'),
                          pygame.image.load('Sprites/Characters/L4.png'),
                          pygame.image.load('Sprites/Characters/L5.png'),
                          pygame.image.load('Sprites/Characters/L6.png'),
                          pygame.image.load('Sprites/Characters/L7.png'),
                          pygame.image.load('Sprites/Characters/L8.png'),
                          pygame.image.load('Sprites/Characters/L9.png')]

    def player_movement(self, keys):
        if keys[pygame.K_q] and self.weapon:
            if self.weapon.new_bullet:
                self.weapon.fire()
                if self.weapon:
                    self.weapon.new_bullet = False
                    thread = Thread(target=self.weapon.rof, daemon=True)
                    thread.start()
        if keys[pygame.K_e]:
            self.grab_weapon()
        if keys[pygame.K_s] and self.weapon:
            drop_thread = Thread(target=self.weapon.drop, daemon=True)
            drop_thread.start()
        if keys[pygame.K_a]:
            self.x -= self.velocity
            self.left, self.right, self.standing = True, False, False
            if self.weapon:
                self.weapon.left, self.weapon.right = True, False
        elif keys[pygame.K_d]:
            self.x += self.velocity
            self.left, self.right, self.standing = False, True, False
            if self.weapon:
                self.weapon.left, self.weapon.right = False, True
        else:
            self.standing, self.walk_count = True, 0
        if not self.jumping and not self.jumped_once:
            if keys[pygame.K_w]:
                self.jumping = True
        elif self.jumping and not self.jumped_once:
            if self.jump_count >= -10:
                neg = 1
                if self.jump_count <= 0:
                    self.jump_count = 10
                    self.jumping = False
                    self.jumped_once = True
                else:
                    self.y -= int((self.jump_count ** 2) * 0.5 * neg)
                    self.jump_count -= 1
            else:
                self.jump_count = 10
                self.jumping = False
