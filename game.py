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
platform = pygame.sprite.Group()
ball = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


class Player(pygame.sprite.Sprite):
    def __init__(self,
                 pos_x=WIDTH // 2,
                 pos_y=HEIGHT - 20,
                 speed=10):
        super().__init__(all_sprites, platform)
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

def main():
    player = Player()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
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
