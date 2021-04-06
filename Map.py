import pygame
from random import choice, randint
from Player import Ice, Fire
from Weapons import M16, L96, Minigun
from PowerUps import HealthPowerUp, InfiniteAmmoPowerUp, ShieldPowerUp
from threading import Thread
from time import sleep


class Game:
    def __init__(self, width, height):
        self.initialize_game()
        self.window = pygame.display.set_mode((width, height))
        self.background = None
        self.start_points = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.bullets_in_screen = []
        self.weapons_in_screen = []
        self.health_bars_in_screen = []
        self.power_ups_in_screen = []
        self.max_weapons_in_screen = 4
        self.max_power_ups_in_screen = 2
        self.endgame = False
        self.player1 = Ice(788, 257, 29, 52, 7, width, height, self)
        self.player2 = Fire(320, 257, 29, 52, 7, width, height, self)
        thread = Thread(target=self.weapons_and_power_ups_thread, daemon=True)
        thread.start()

    @staticmethod
    def initialize_game():
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Game")
        pygame.mixer.set_num_channels(8)

    def redraw_window(self, window, background):
        window.blit(background, (0, 0))
        self.player1.player_drawing(window)
        self.player2.player_drawing(window)
        for bullet in self.bullets_in_screen:
            bullet.draw_projectile(window)
        for weapon in self.weapons_in_screen:
            weapon.draw_weapon(window)
        for health_bar in self.health_bars_in_screen:
            health_bar.draw_health_bar(window)
        for power_up in self.power_ups_in_screen:
            power_up.draw_power_up(window)
        pygame.display.update()

    def respawn_player(self, player):
        start_point = choice(self.start_points)
        player.initialize_respawn(start_point[0], start_point[1])
        thread = Thread(target=player.levitate, daemon=True)
        thread.start()

    def spawn_weapons(self):
        if len(self.weapons_in_screen) <= self.max_weapons_in_screen:
            spawn = randint(200, 900)
            facing = choice(['R', 'L'])
            weapon = choice([M16, L96, Minigun])
            self.weapons_in_screen.append(weapon(spawn, -100, facing))

    def weapons_and_power_ups_thread(self):
        while True:
            sleep(4)
            weapon = choice([True, False])
            if weapon:
                self.spawn_weapons()
            power_up = choice([True, False, False])
            if power_up:
                self.spawn_power_ups()

    def spawn_power_ups(self):
        if len(self.power_ups_in_screen) <= self.max_power_ups_in_screen:
            spawn = choice([[randint(200, 930), 263], [randint(290, 450), 156],
                            [randint(680, 840), 156], [randint(490, 640), 43]])
            power_up = choice([HealthPowerUp, InfiniteAmmoPowerUp, ShieldPowerUp])
            self.power_ups_in_screen.append(power_up(spawn[0], spawn[1]))

    # noinspection PyUnresolvedReferences
    def run(self):
        while self.running:
            self.clock.tick(40)

            if self.endgame:
                self.running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == 2 and event.dict['key'] == 27):
                    self.running = False
                if event.type == 5:
                    print(event.pos)

            for bullet in self.bullets_in_screen:
                if bullet.shot_by == self.player1:
                    if bullet.x + int(bullet.width / 2) in\
                            range(self.player2.hitbox[0], self.player2.hitbox[0] + self.player2.hitbox[2])\
                            and bullet.y + int(bullet.height / 2) in\
                            range(self.player2.hitbox[1], self.player2.hitbox[1] + self.player2.hitbox[3]):
                        self.player2.shot(bullet)
                        self.bullets_in_screen.pop(self.bullets_in_screen.index(bullet))
                if bullet.shot_by == self.player2:
                    if bullet.x + int(bullet.width / 2) in \
                            range(self.player1.hitbox[0], self.player1.hitbox[0] + self.player1.hitbox[2]) \
                            and bullet.y + int(bullet.height / 2) in \
                            range(self.player1.hitbox[1], self.player1.hitbox[1] + self.player1.hitbox[3]):
                        self.player1.shot(bullet)
                        self.bullets_in_screen.pop(self.bullets_in_screen.index(bullet))

                if not bullet.erased:
                    bullet.x += bullet.velocity
                else:
                    self.bullets_in_screen.pop(self.bullets_in_screen.index(bullet))

            for weapon in self.weapons_in_screen:
                if not weapon.erased:
                    if weapon.falling:
                        self.weapon_physics(weapon)
                else:
                    self.weapons_in_screen.pop(self.weapons_in_screen.index(weapon))

            for power_up in self.power_ups_in_screen:
                if not power_up.erased:
                    if power_up.x + int(power_up.width / 2) in\
                            range(self.player1.hitbox[0], self.player1.hitbox[0] + self.player1.hitbox[2])\
                            and power_up.y + int(power_up.height / 2) in\
                            range(self.player1.hitbox[1], self.player1.hitbox[1] + self.player1.hitbox[3]):
                        power_up.user = self.player1
                        self.power_ups_in_screen.pop(self.power_ups_in_screen.index(power_up))
                        power_up.power_up_thread()
                    elif power_up.x + int(power_up.width / 2) in\
                            range(self.player2.hitbox[0], self.player2.hitbox[0] + self.player2.hitbox[2])\
                            and power_up.y + int(power_up.height / 2) in\
                            range(self.player2.hitbox[1], self.player2.hitbox[1] + self.player2.hitbox[3]):
                        power_up.user = self.player2
                        self.power_ups_in_screen.pop(self.power_ups_in_screen.index(power_up))
                        power_up.power_up_thread()
                else:
                    self.power_ups_in_screen.pop(self.power_ups_in_screen.index(power_up))

            keys = pygame.key.get_pressed()
            self.player1.player_movement(keys)
            self.player2.player_movement(keys)
            self.player_physics(self.player1)
            self.player_physics(self.player2)
            self.redraw_window(self.window, self.background)

        pygame.quit()


class FirstStage(Game):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.background = pygame.image.load('Sprites/Background.jpg')
        self.start_points = [[349, 0], [745, 0]]
        pygame.mixer.music.load('Sounds/PlatypusLevel4.wav')
        pygame.mixer.music.play(-1)

    # noinspection PyMethodMayBeStatic
    def player_physics(self, player):
        if player.x + int(player.width / 2) in range(193, 940) and player.y + player.height in range(287, 340):
            player.y = 263
            player.jumped_once = False
            player.fall_count = 0
        elif player.x + int(player.width / 2) in range(193, 940) and player.y in range(287, 340):
            player.y = 345
            player.jumped_once = False
            player.fall_count = 0
        elif (player.x + int(player.width / 2) in range(270, 458)
              or player.x + int(player.width / 2) in range(660, 850))\
                and player.y + player.height in range(200, 230):
            player.y = 157 if not player.jumping else player.y
            player.jumped_once = False
            player.fall_count = 0
        elif player.x + int(player.width / 2) in range(472, 652) and player.y + player.height in range(90, 120):
            player.y = 47 if not player.jumping else player.y
            player.jumped_once = False
            player.fall_count = 0
        else:
            if not player.jumping:
                player.y += player.incremental_fall[player.fall_count] if player.fall_count <= 44 else 15
                player.fall_count += 1
            player.y += 1  # Just in case

    # noinspection PyMethodMayBeStatic
    def weapon_physics(self, weapon):
        if (weapon.x in range(270, 458) or weapon.x in range(660, 850)) and weapon.y in range(166, 183):
            weapon.falling = False
        elif weapon.x in range(472, 652) and weapon.y in range(60, 83):
            weapon.falling = False
        elif weapon.x in range(193, 940) and weapon.y in range(287, 340):
            weapon.falling = False
        else:
            if weapon.falling:
                weapon.y += 2
