import pygame
import random

import pygame
import random


class Rectangle_effect:
    rects = []
    timer = 0

    def __init__(self, pos, size, speed, dirs):
        self.pos = pos
        self.size = size
        self.speed = speed
        self.dirs = dirs  # True for going up False for down

    def move(self, display, palette):
        sur = pygame.Surface(self.size)
        sur.fill(palette.palette["backgroundShade"])
        sur.set_alpha(random.randint(100, 200))
        display.blit(sur, self.pos)

        if self.dirs[0]:
            self.pos[1] -= self.speed
        elif self.dirs[1]:
            self.pos[1] += self.speed
        elif self.dirs[2]:
            self.pos[0] += self.speed
        elif self.dirs[3]:
            self.pos[0] -= self.speed

        if self.pos[1] < -120 or self.pos[0] > 600 or self.pos[1] > 650 or self.pos[0] < -120:
            self.delete(self)

    @classmethod
    def generate_rects(cls, amount=100, speed_range=None):
        if speed_range is None:
            speed_range = [1, 4]

        for _ in range(amount):
            dirs = [0, 0, 0, 0]
            dirs[random.randint(0, 3)] = 1
            cls.rects.append(Rectangle_effect([random.randint(0, 600), random.randint(0, 650)],
                                              [random.randint(40, 120), random.randint(40, 120)],
                                              random.randint(speed_range[0], speed_range[1]),
                                              dirs))

    @classmethod
    def delete(cls, circle):
        cls.rects.remove(circle)
