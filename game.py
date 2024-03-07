import pygame
import random
import sys
import os

FPS = 120
WIDTH = 1024
HEIGHT = 768

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Game for lyceum project')

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
balls = pygame.sprite.Group()
bricks = pygame.sprite.Group()

basic_font = pygame.font.Font('freesansbold.ttf', 20)
score_color = (125, 125, 125)

bricks_count = 10
b_width = WIDTH // bricks_count
b_height = 30
platform_height = 30


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    """Функция для загрузки изображений"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


brick_pic = {'blue': load_image('blue_brick.png'),
             'yellow': load_image('yellow_brick.png'),
             'red': load_image('red_brick.png')}


def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_file = [line.strip() for line in mapFile]
    except FileNotFoundError:
        print('Указанный файл не существует')
        terminate()
    return level_file


class Brick(pygame.sprite.Sprite):
    def __init__(self, brick_type, pos_x, pos_y, health=10):
        super().__init__(all_sprites, bricks)
        self.image = pygame.transform.scale(brick_pic[brick_type], (b_width, b_height))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.health = health

    def hit(self):
        self.health -= 10

    def update(self):
        if self.health < 0:
            self.kill()
            print(all_sprites.__len__())


def generate_level(level):
    level_data = load_level(f'level_{level}.txt')
    for num_y, line in enumerate(level_data):
        for num_x, brick_t in enumerate(line):
            if brick_t == '@':
                Brick('blue', num_x * b_width, num_y * b_height, health=10)
            if brick_t == '#':
                Brick('yellow', num_x * b_width, num_y * b_height, health=20)
            if brick_t == '$':
                Brick('red', num_x * b_width, num_y * b_height, health=30)


class Player(pygame.sprite.Sprite):
    def __init__(self,
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - 30 - platform_height,  # отступ для статус-бара (30 - выс.стат.бара)
                 speed=10):
        super().__init__(all_sprites, platforms)
        self.image = pygame.transform.scale(load_image('platform.png'), (120, platform_height))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery += pos_y
        self.speed = speed
        self.movement = 0

    def screen_borders(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def update(self):
        self.rect.centerx += self.movement
        self.screen_borders()


class Ball(pygame.sprite.Sprite):
    def __init__(self,
                 game,
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - 30 - platform_height,  # отступ для статус-бара
                 speed_x=5,
                 speed_y=5,
                 active=False):
        super().__init__(all_sprites, balls)
        self.active = active
        self.image = pygame.transform.scale(load_image('ball.png'), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.bottom = pos_y
        self.speed_x = speed_x * random.choice((-1, 1))
        # добавляем элемент случайности
        self.speed_y = speed_y - ((random.randrange(15) / 10) * random.choice((-1, 1)))
        self.game = game

    def update(self):
        if self.active:
            self.rect.centerx += self.speed_x
            self.rect.centery -= self.speed_y
            self.collisions()

    def collisions(self):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT - 30:
            self.speed_y *= -1
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1

        if pygame.sprite.spritecollide(self, platforms, False):
            self.speed_y *= -1
            self.game.add_score()

        col_brick = pygame.sprite.spritecollide(self, bricks, False)
        if col_brick:
            col_brick[0].hit()
            self.speed_y *= -1
            self.game.add_score()


class Game:
    def __init__(self):
        self.score = 0
        self.score_step = 10

    def add_score(self):
        self.score += self.score_step

    def draw_score(self):
        player_score = basic_font.render(f'Очки: {str(self.score)}', True, score_color)
        player_score_rect = player_score.get_rect(midleft=(10, HEIGHT - 13))
        screen.blit(player_score, player_score_rect)

    def check_end_of_lvl(self):
        if len(bricks) < 1:
            print('end of game')
            for ball in balls:
                ball.kill()

    def update(self):
        self.draw_score()
        self.check_end_of_lvl()


def main():
    game = Game()
    player = Player()
    ball = Ball(game=game)
    generate_level(1)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ball.active = True
                if event.key == pygame.K_LEFT:
                    player.movement -= player.speed
                if event.key == pygame.K_RIGHT:
                    player.movement += player.speed
                if event.key == pygame.K_b:
                    for _ in range(20):
                        Ball(game=game, active=True)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.movement += player.speed
                if event.key == pygame.K_RIGHT:
                    player.movement -= player.speed

        screen.fill(pygame.Color(0, 0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        game.update()
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


if __name__ == '__main__':
    main()
