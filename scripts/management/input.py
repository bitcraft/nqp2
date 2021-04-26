import pygame
from pygame.locals import *

class Input:
    def __init__(self, game):
        self.game = game

        self.states = {
            'right': False,
            'left': False,
        }

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.game.quit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game.quit()

                if event.key == K_RIGHT:
                    self.states['right'] = True

                if event.key == K_LEFT:
                    self.states['left'] = True
