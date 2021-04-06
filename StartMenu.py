import pygame


class StartScreen:
    def __init__(self, width, height):
        self.initialize_game()
        self.window = pygame.display.set_mode((width, height))
        self.background = pygame.image.load('Sprites/StartBackground.jpg')
        self.clock = pygame.time.Clock()
        self.running = True
        self.endgame = False
        self.width = width
        self.height = height
        self.start = Start(self.width // 2, self.height // 2)

    @staticmethod
    def initialize_game():
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Game")
        pygame.mixer.set_num_channels(8)

    def redraw_window(self):
        self.window.blit(self.background, (0, 0))
        self.start.draw_button(self.window)
        pygame.display.update()

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

            self.redraw_window()

        pygame.quit()


class Button:
    def __init__(self, x, y):
        self.width = 110
        self.height = 50
        self.x = x - self.width // 2
        self.y = y - self.height // 2
        self.text = None
        self.hitbox = (self.x, self.y, self.width, self.height)

    # noinspection PyUnresolvedReferences
    def draw_button(self, window):
        pygame.draw.rect(window, self.color, self.hitbox)


class Start(Button):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 0, 0)
