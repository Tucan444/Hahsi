import pygame
import math


class Button:

    def __init__(self, pos, size, images, onclick=None, onclick_args=None, active=True):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.images = images
        self.display_image = images["idle"]
        self.on_click = onclick
        self.oc_args = onclick_args
        self.active = active
        self.switch_images = None
        self.name = ""

    def hover_check(self, mouse_pos):
        if self.active:
            if self.rect.collidepoint(mouse_pos):
                self.display_image = self.images["hover"]
            else:
                self.display_image = self.images["idle"]

    def click_check(self, mouse_pos):
        if self.active:
            if self.rect.collidepoint(mouse_pos):
                if self.on_click is not None:
                    self.on_click(self.oc_args)

    def blit(self, display, scroll=None):
        if self.active:
            if scroll is None:
                display.blit(self.display_image, self.pos)
            else:
                display.blit(self.display_image, [self.pos[0] - scroll.scroll[0],
                                                  self.pos[1] - scroll.scroll[1]])

    def switch(self, mouse_pos):
        self.switch_images, self.images = self.images, self.switch_images
        self.hover_check(mouse_pos)

    def move(self, movement):
        self.pos = [self.pos[0] + movement[0],
                    self.pos[1] + movement[1]]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])


class CircleButton:
    def __init__(self, size, pos, images, onclick=None, onclick_args=None, active=True):
        self.pos = pos
        self.size = size
        self.center = [pos[0] + (size/2), pos[1] + (size/2)]
        self.radius = size/2
        self.images = images
        self.display_image = images["idle"]
        self.on_click = onclick
        self.oc_args = onclick_args
        self.active = active
        self.switch_images = None
        self.name = ""

    def hover_check(self, mouse_pos):
        if self.active:
            if distance_indicator(self.center, mouse_pos) <= self.radius:
                self.display_image = self.images["hover"]
            else:
                self.display_image = self.images["idle"]

    def click_check(self, mouse_pos):
        if self.active:
            if distance_indicator(self.center, mouse_pos) <= self.radius:
                if self.on_click is not None:
                    self.on_click(self.oc_args)

    def blit(self, display, scroll=None):
        if self.active:
            if scroll is None:
                display.blit(self.display_image, self.pos)
            else:
                display.blit(self.display_image, [self.pos[0] - scroll.scroll[0],
                                                  self.pos[1] - scroll.scroll[1]])

    def switch(self, mouse_pos):
        self.switch_images, self.images = self.images, self.switch_images
        self.hover_check(mouse_pos)

    def move(self, movement):
        self.pos = [self.pos[0] + movement[0],
                    self.pos[1] + movement[1]]
        self.center = [self.pos[0] + (self.size / 2), self.pos[1] + (self.size / 2)]


def distance_indicator(cords1, cords2):
    x_distance = abs(cords1[0] - cords2[0])
    y_distance = abs(cords1[1] - cords2[1])
    distance = round(math.sqrt((x_distance**2) + (y_distance**2)))
    return distance
