import pygame
from pygame.locals import *

pygame.init()


def get_sounds():
    sounds = {"click": pygame.mixer.Sound("assets/sounds/click.wav"),
              "remove": pygame.mixer.Sound("assets/sounds/remove.wav"),
              "join": pygame.mixer.Sound("assets/sounds/join.wav")}

    return sounds
