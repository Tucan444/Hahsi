import pygame
import random


class Circle_effect:

    circles = []
    timer = 0

    def __init__(self, pos, radius, speed, vertical):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.vertical = vertical  # True for going up False for down

    def move(self, display, palette, horizontal=False):
        sur = pygame.Surface((self.radius * 2, self.radius * 2))
        pygame.draw.circle(sur, palette.palette["addition"], [self.radius, self.radius], self.radius)
        sur.set_alpha(random.randint(100, 200))
        sur.set_colorkey((0, 0, 0))
        display.blit(sur, self.pos)

        if self.vertical:
            if horizontal:
                self.pos[0] -= self.speed
            else:
                self.pos[1] -= self.speed
        else:
            if horizontal:
                self.pos[0] += self.speed
            else:
                self.pos[1] += self.speed

        if self.pos[1] < -100 or self.pos[0] > 700 or self.pos[1] > 700 or self.pos[0] < -100:
            self.delete(self)

    @classmethod
    def generate_circles(cls, amount=100, y_lim=None):
        if y_lim is None:
            y_lim = [0, 100]

        for _ in range(amount):
            cls.circles.append(Circle_effect([random.randint(y_lim[0], y_lim[1]), random.randint(0, 650)],
                                             random.randint(20, 50), random.randint(1, 4),
                                             [True if x == 1 else False for x in [random.randint(0, 1)]][0]))

    @classmethod
    def delete(cls, circle):
        cls.circles.remove(circle)

