import pygame
import random
import sys
import os

FPS = 50
WIDTH = 1024
HEIGHT = 768

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Game for lyceum project')

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
balls = pygame.sprite.Group()


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


class Player(pygame.sprite.Sprite):
    def __init__(self,
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - 20,
                 speed=10):
        super().__init__(all_sprites, platforms)
        self.image = pygame.Surface((100, 20))
        self.image.fill((125, 125, 125))
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
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - 20,
                 speed_x=5,
                 speed_y=5        ):
        super().__init__(all_sprites, balls)
        self.active = False
        self.image = pygame.transform.scale(load_image('ball.png'), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.bottom = pos_y
        self.speed_x = speed_x * random.choice((-1,1))
        # добавляем элемент случайности
        self.speed_y = speed_y - ((random.randrange(15) / 10) * random.choice((-1,1)))

    def update(self):
        if self.active:
            self.rect.centerx += self.speed_x
            self.rect.centery -= self.speed_y
            self.collisions()

    def collisions(self):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1

        if pygame.sprite.spritecollide(self, platforms, False):
            self.speed_y *= -1


def main():
    player = Player()
    ball = Ball()
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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.movement += player.speed
                if event.key == pygame.K_RIGHT:
                    player.movement -= player.speed

        screen.fill(pygame.Color(0, 0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


if __name__ == '__main__':
    main()
