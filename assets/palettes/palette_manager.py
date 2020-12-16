import os
import json
import pygame
from itertools import cycle
pygame.init()


class Palettes:
    def __init__(self, path):
        self.path = path
        self.palettes = {}
        self.current_palette = "emerald"  # set starting palette here
        self.load_palettes()
        self.palette = self.get_palette()
        self.cycle = None
        self.changed = False

    def load_palettes(self):
        current_dir = os.getcwd()
        os.chdir(self.path)
        files = os.listdir()
        files.remove('palette_manager.py')
        try:
            files.remove("__pycache__")
        except:
            pass

        for file in files:
            with open(file, "r") as f:
                fileX = json.load(f)

            for color in fileX.keys():
                fileX[color] = self.rgb(fileX[color])

            file = "".join(list(file)[:-5])

            self.palettes[file] = fileX

        os.chdir(current_dir)

    def get_palette(self):
        return self.palettes[self.current_palette]

    def swap_image(self, image, old_p, new_p):
        for color in self.palettes[old_p].keys():
            image = swap_color(image, self.palettes[old_p][color], self.palettes[new_p][color])

        return image

    def create_cycle(self):
        names = self.palettes.keys()
        self.cycle = cycle(names)
        while next(self.cycle) != self.current_palette:
            pass

    @staticmethod
    def rgb(color):
        color = color.strip("#")
        color = [int(color[i:i+2], 16) for i in range(0, 5, 2)]
        return color


def swap_color(imageX, old, new):
    image_copy = pygame.Surface(imageX.copy().get_size())
    image_copy.fill(new)

    imageX.set_colorkey(old)

    image_copy.blit(imageX, [0, 0])

    return image_copy
