import pygame
from random import randrange, choice
import sys
import os

FPS = 120
WIDTH = 1024
HEIGHT = 768

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Game for lyceum project')

pygame.mixer.pre_init(44100, -16, 2, 512)
plob_sound = pygame.mixer.Sound("data/pong.wav")
lost_sound = pygame.mixer.Sound("data/lostball.wav")
bonus_sound = pygame.mixer.Sound("data/bonus.wav")
game_over_sound = pygame.mixer.Sound("data/gameover.ogg")

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
balls = pygame.sprite.Group()
bricks = pygame.sprite.Group()
bonuses = pygame.sprite.Group()

BG_COLOR = pygame.Color(33, 34, 54)
BASIC_FONT = pygame.font.Font('freesansbold.ttf', 20)
SCORE_COLOR = (125, 125, 125)

bricks_count = 10
b_width = WIDTH // bricks_count
b_height = 30
platform_height = 30
stat_bar_height = 30

cap_lvl = 6


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
    """Функция для загрузки уровней из файла"""
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
        if self.health <= 0:
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
    """Платформа игрока"""
    def __init__(self,
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - stat_bar_height - platform_height,  # отступ для статус-бара
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
                 pos_y=HEIGHT - stat_bar_height - platform_height,  # отступ для статус-бара
                 speed_x=5,
                 speed_y=5,
                 active=False):
        super().__init__(all_sprites, balls)
        self.active = active
        self.image = pygame.transform.scale(load_image('ball.png'), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.bottom = pos_y
        self.speed_x = speed_x * choice((-1, 1))
        # добавляем элемент случайности
        self.speed_y = speed_y - ((randrange(15) / 10) * choice((-1, 1)))
        self.game = game  # экземпляр класса Game

    def stop(self):
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT - stat_bar_height - platform_height

    def update(self):
        if self.active:
            self.rect.centerx += self.speed_x
            self.rect.centery -= self.speed_y
            self.collisions()
        else:
            for _ in platforms:
                self.rect.centerx = self.game.player.rect.centerx

    def collisions(self):
        """Столкновения мяча с другими объектами"""
        if self.rect.top <= 0:
            self.speed_y *= -1
            self.speed_y = self.speed_y  # - ((random.randrange(10) / 10) * random.choice((-1, 1)))
        if self.rect.bottom >= HEIGHT - stat_bar_height:
            pygame.mixer.Sound.play(lost_sound)
            for b in balls:
                b.kill()  # удаляем все мячи для исключения повторного вычитания жизней
            self.game.skip_the_ball()

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1

        col_platform = pygame.sprite.spritecollide(self, platforms, False)
        if col_platform:
            pygame.mixer.Sound.play(plob_sound)
            self.rect.bottom = col_platform[0].rect.y  # убираем баг с ударом в бок платформы
            self.speed_y *= -1
            self.speed_y -= ((randrange(10) / 10) * choice((-1, 1)))
            self.game.add_score()
            # print(f'>>2')

        col_brick = pygame.sprite.spritecollide(self, bricks, False)
        if col_brick:
            pygame.mixer.Sound.play(plob_sound)
            col_brick[0].hit()
            self.speed_y *= -1
            self.speed_y = self.speed_y
            self.game.add_score()
            if randrange(0, 100) <= 1:
                pygame.mixer.Sound.play(bonus_sound)
                Bonuses(self.game, randrange(1, 3), self.rect.centerx, self.rect.centery, 50, 50, 4)
            # print(f'>>3')


class Bonuses(pygame.sprite.Sprite):
    """Класс для выпадающих бонусов"""
    def __init__(self, game, type_of_bonuse, pos_x, pos_y, w, h, frame_count):
        super().__init__(all_sprites, bonuses)
        self.type_of_bonuse = type_of_bonuse
        self.frames = [pygame.transform.scale(load_image(f'b{self.type_of_bonuse}_{i}.png'),
                                              (w, h)) for i in range(frame_count)]
        self.fr_count = 0
        self.frame_count = frame_count
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.game = game

    def collisions(self):
        if pygame.sprite.spritecollide(self, platforms, False):
            if self.type_of_bonuse == 1:
                self.game.lives += 1
                self.kill()
            if self.type_of_bonuse == 2:
                self.kill()
                pygame.mixer.Sound.play(lost_sound)
                for b in balls:
                    b.kill()  # удаляем все мячи для исключения повторного вычитания жизней
                self.game.skip_the_ball()

    def update(self):
        self.fr_count = (self.fr_count + 0.02) % self.frame_count
        self.image = self.frames[int(self.fr_count)]
        self.rect.centery += 1
        self.collisions()


class SetScreen:
    def __init__(self, pic_name, text, x, y):
        self.pic_name = pic_name
        self.text_msg = text
        self.pos_x = x
        self.pos_y = y

    def set_screen(self):
        background = pygame.transform.scale(load_image(self.pic_name), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        font = pygame.font.Font(None, 30)
        for line in self.text_msg:
            string_rendered = font.render(line, True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = self.pos_y
            intro_rect.x = self.pos_x
            screen.blit(string_rendered, intro_rect)
            self.pos_y += intro_rect.height + 10
        pygame.display.flip()


class Game:

    def __init__(self):
        self.score = 0
        self.score_step = 10
        self.player = Player()
        self.lvl = 1
        self.lives = 3
        self.ball = None
        self.start_g = False
        self.start_script()

    def add_score(self):
        self.score += self.score_step

    def skip_the_ball(self):
        self.ball = Ball(game=self)
        self.lives -= 1
        print(f'lives = {self.lives}')
        if self.lives == 0:
            pygame.mixer.Sound.play(game_over_sound)
            self.restart_game()
            SetScreen('gameover.jpg', ['Для начала игры нажмите Space'], 350, 60).set_screen()

    def draw_score(self):
        player_score = BASIC_FONT.render(f'Очки: {str(self.score)}      Уровень: {self.lvl}     '
                                         f'Жизни: {self.lives}', True, SCORE_COLOR)
        player_score_rect = player_score.get_rect(midleft=(10, HEIGHT - 13))
        screen.blit(player_score, player_score_rect)

    def check_end_of_lvl(self):
        if len(bricks) < 1:
            print('end of lvl')
            for b in balls:
                b.kill()
            self.lvl = self.lvl + 1
            if self.lvl >= cap_lvl:
                self.lvl = cap_lvl
            self.start()

    def start(self):
        for b in bonuses:
            b.kill()  # убираем все бонусы
        generate_level(self.lvl)
        self.ball = Ball(game=self)

    def restart_game(self):
        for i in all_sprites:
            i.kill()
        self.score = 0
        self.score_step = 10
        self.player = Player()
        self.lvl = 1
        self.lives = 3
        self.ball = None
        self.start_g = False
        self.start()

    def start_script(self):
        SetScreen('start_screen.jpg', ['Проект для аттестации',
                                       'Для начала игры нажмите Space (пробел)',
                                       'Для запуска мяча нажмите Space (пробел)'], 300, 130).set_screen()
        self.start()

    def update(self):
        if self.start_g:
            screen.fill(BG_COLOR)
            self.draw_score()
            self.check_end_of_lvl()
            all_sprites.draw(screen)
            all_sprites.update()
            pygame.display.flip()
            clock.tick(FPS)
            # print(len(balls))


def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                print(f'pygame.KEYDOWN = {event.type == pygame.KEYDOWN} mov = {game.player.movement}')
                if event.key == pygame.K_RETURN:
                    pass  # game.start_g = True
                if event.key == pygame.K_SPACE:
                    if game.start_g:  # если игра началась, запускаем шар
                        game.ball.active = True
                    else:
                        game.start_g = True
                if event.key == pygame.K_LEFT and game.start_g:
                    game.player.movement -= game.player.speed
                if event.key == pygame.K_RIGHT and game.start_g:
                    game.player.movement += game.player.speed
                if event.key == pygame.K_b and game.start_g:
                    for _ in range(10):
                        Ball(game=game, active=True)
            if event.type == pygame.KEYUP and game.start_g:
                print(f'pygame.KEYUP = {event.type == pygame.KEYUP} mov = {game.player.movement}')
                if event.key == pygame.K_LEFT and game.start_g:
                    game.player.movement += game.player.speed
                if event.key == pygame.K_RIGHT and game.start_g:
                    game.player.movement -= game.player.speed

        game.update()
    terminate()


if __name__ == '__main__':
    main()
