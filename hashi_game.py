import json
import sounds
import widget_engine as wg
from hashi_functions import get_num_circles
from hashi_functions import get_images
import pygame
import math
import copy


pygame.init()

soundsX = sounds.get_sounds()


class HashiG:

    def __init__(self, load_from_where, load_path, palette, mouse):
        # creating variables
        self.map = []
        self.size = None
        self.indent = 40
        self.indent_default = 40
        self.node_count = 0
        self.win = False

        # for nodes
        self.locked = False
        self.c_node = None
        self.temp_done = [0, 0, 0, 0]
        self.temp_removed = [0, 0, 0, 0]
        self.s_node = None

        # loading game
        if load_from_where == "file.txt":
            self.load_from_file(load_path, palette)
        elif load_from_where == "file.json":
            self.load_game(load_path, palette, mouse)

        self.set_size()
        self.line_width = int(self.indent / 12) + 1

    def load_from_file(self, path, palette):
        with open(path, "r") as f:
            file = f.read()
            f.close()

        file = file.split("\n")
        del file[-1]

        # init blank map
        self.size = len(file)
        self.map = [[NodeG([x, y]) for y in range(len(file))] for x in range(len(file))]
        self.set_size()

        # getting images
        images, widget_size = get_num_circles(palette, math.sqrt(self.indent/self.indent_default)**1.5)
        switch_images = get_images(palette, widget_size)

        # reversing to get back into our format
        file = file[::-1]
        file = [x.split() for x in file]
        for y in range(len(file)):
            for x in range(len(file[y])):
                node = self.map[x][y]
                node.bridge_num = int(file[y][x])
                if int(file[y][x]) != 0:
                    # if its node and not blank

                    node.locked = True
                    node.widget = wg.CircleButton(widget_size, [0, 0],
                                                  images[file[y][x]], self.lock, [node])
                    node.widget.switch_images = switch_images[file[y][x]]
                    self.node_count += 1

    def load_game(self, path, palette, mouse):

        with open(path, "r") as f:
            save = json.load(f)

        self.load_from_file(f"assets/maps/{save['difficulty']}.txt", palette)

        for connection in save["connections"]:
            # also bridge_occupied
            if self.map[connection["pos"][0]][connection["pos"][1]].bridge_num != 0:
                self.map[connection["pos"][0]][connection["pos"][1]].bridges = connection["bridges"]
                self.map[connection["pos"][0]][connection["pos"][1]].bridge_occupied = connection["bridge_occupied"]
                self.map[connection["pos"][0]][connection["pos"][1]].locked = connection["locked"]
                if self.map[connection["pos"][0]][connection["pos"][1]].bridge_occupied == self.map[connection["pos"][0]][connection["pos"][1]].bridge_num:
                    if self.map[connection["pos"][0]][connection["pos"][1]].widget is not None:
                        self.map[connection["pos"][0]][connection["pos"][1]].widget.switch(mouse.mouse_pos)
            else:
                self.map[connection["pos"][0]][connection["pos"][1]].locked = connection["locked"]

    def blit(self, display, palette, scroll):
        # grid
        for lines in range(self.size):
            pygame.draw.line(display, palette.palette["outline-shade"],
                             [(lines * self.indent) - scroll.scroll[0],
                              0 - scroll.scroll[1]],
                             [(lines * self.indent) - scroll.scroll[0],
                              ((self.size - 1) * self.indent) - scroll.scroll[1]], self.line_width)
            pygame.draw.line(display, palette.palette["outline-shade"],
                             [0 - scroll.scroll[0],
                              (lines * self.indent) - scroll.scroll[1]],
                             [((self.size - 1) * self.indent) - scroll.scroll[0],
                              (lines * self.indent) - scroll.scroll[1]], self.line_width)

        # connections
        for x in range(self.size):
            for y in range(self.size):
                for connection in self.map[x][y].bridges:
                    if connection["connection"] is not None:
                        if connection["bridge_num"] == 1:
                            node = self.map[x][y]
                            target = self.map[connection["connection"][0]][connection["connection"][1]]
                            pygame.draw.line(display, palette.palette["addition"],
                                             [(node.pos[0] * self.indent) - scroll.scroll[0],
                                              (node.pos[1] * self.indent) - scroll.scroll[1]],
                                             [(target.pos[0] * self.indent) - scroll.scroll[0],
                                              (target.pos[1] * self.indent) - scroll.scroll[1]],
                                             self.line_width + 1)
                        elif connection["bridge_num"] == 2:
                            node = self.map[x][y]
                            target = self.map[connection["connection"][0]][connection["connection"][1]]
                            pygame.draw.line(display, palette.palette["outline-dark"],
                                             [(node.pos[0] * self.indent) - scroll.scroll[0],
                                              (node.pos[1] * self.indent) - scroll.scroll[1]],
                                             [(target.pos[0] * self.indent) - scroll.scroll[0],
                                              (target.pos[1] * self.indent) - scroll.scroll[1]],
                                             int((self.line_width * 1.4) + 1))

        # dealing with nodes
        for x in range(self.size):
            for y in range(self.size):
                if self.map[x][y].widget is not None:
                    node = self.map[x][y]
                    node.widget.pos = [(node.pos[0] * self.indent) - node.widget.radius,
                                       (node.pos[1] * self.indent) - node.widget.radius]
                    node.widget.center = [node.widget.pos[0] + node.widget.radius,
                                          node.widget.pos[1] + node.widget.radius]
                    node.widget.blit(display, scroll)

    def hover(self, mouse, scroll):
        ms = mouse.get_scrolled(scroll)

        for y in range(self.size):
            for x in range(self.size):
                if self.map[x][y].widget is not None:
                    self.map[x][y].widget.hover_check(ms)

    def click(self, mouse, scroll):
        ms = mouse.get_scrolled(scroll)

        for y in range(self.size):
            for x in range(self.size):
                if self.map[x][y].widget is not None:
                    self.map[x][y].widget.click_check(ms)

    def on_locked(self, mouse, scroll):
        ms = mouse.get_scrolled(scroll)
        cords = self.c_node.pos

        dists = [ms[0] - self.c_node.widget.center[0],
                 ms[1] - self.c_node.widget.center[1]]
        da = list(map(abs, dists))
        self.clear_temp()
        self.clear_temp_remove()

        # if we still can add bridges
        if self.c_node.bridge_occupied < self.c_node.bridge_num:

            # if we move out mouse more on x
            if da[0] > da[1]:
                if dists[0] > 0:
                    # here we do in case we move right

                    self.__right(cords)

                else:
                    # here we do in case we move left

                    self.__left(cords)
            else:

                if dists[1] > 0:
                    # here we do in case we move down

                    self.__down(cords)
                else:
                    # here we do in case we go up

                    self.__up(cords)
        # removing bridges here
        else:
            if da[0] > da[1]:
                if dists[0] > 0:
                    # here we do in case we move right

                    if self.c_node.bridges[2]["bridge_num"] != 2:
                        for i in range(1, self.size):
                            if cords[0] + i < self.size:
                                if self.map[cords[0] + i][cords[1]].locked is False:
                                    pass

                                else:
                                    if self.map[cords[0] + i][cords[1]].pos == self.c_node.bridges[2]["connection"]:
                                        # connect
                                        self.s_node = self.map[cords[0] + i][cords[1]]

                                        self.c_node.bridges[2]["bridge_num"] -= 1
                                        self.s_node.bridges[3]["bridge_num"] -= 1

                                        if self.c_node.bridges[2]["bridge_num"] == -1:
                                            self.c_node.bridges[2]["bridge_num"] = 0
                                            self.s_node.bridges[3]["bridge_num"] = 0
                                            break

                                        self.temp_removed[2] = 1

                                        if self.c_node.bridges[2]["bridge_num"] == 0:
                                            self.c_node.bridges[2] = {"bridge_num": 0, "connection": True}
                                            self.s_node.bridges[3] = {"bridge_num": 0, "connection": True}

                                        break
                                    else:
                                        if self.c_node.bridges[2]["connection"] is not None and self.map[cords[0] + i][cords[1]].bridge_occupied == 0:
                                            pass
                                        else:
                                            break
                            else:
                                break
                    else:
                        self.__right(cords)

                else:
                    # here we do in case we move left

                    if self.c_node.bridges[3]["bridge_num"] != 2:
                        for i in range(1, self.size):
                            if cords[0] - i > -1:
                                if self.map[cords[0] - i][cords[1]].locked is False:
                                    pass

                                else:
                                    if self.map[cords[0] - i][cords[1]].pos == self.c_node.bridges[3]["connection"]:
                                        # connect
                                        self.s_node = self.map[cords[0] - i][cords[1]]

                                        self.c_node.bridges[3]["bridge_num"] -= 1
                                        self.s_node.bridges[2]["bridge_num"] -= 1

                                        if self.c_node.bridges[3]["bridge_num"] == -1:
                                            self.c_node.bridges[3]["bridge_num"] = 0
                                            self.s_node.bridges[2]["bridge_num"] = 0
                                            break

                                        self.temp_removed[3] = 1

                                        if self.c_node.bridges[3]["bridge_num"] == 0:
                                            self.c_node.bridges[3] = {"bridge_num": 0, "connection": True}
                                            self.s_node.bridges[2] = {"bridge_num": 0, "connection": True}

                                        break
                                    else:
                                        if self.c_node.bridges[3]["connection"] is not None and self.map[cords[0] - i][cords[1]].bridge_occupied == 0:
                                            pass
                                        else:
                                            break
                            else:
                                break
                    else:
                        self.__left(cords)
            else:

                if dists[1] > 0:
                    # here we do in case we move down

                    if self.c_node.bridges[1]["bridge_num"] != 2:
                        for i in range(1, self.size):
                            if cords[1] + i < self.size:
                                if self.map[cords[0]][cords[1] + i].locked is False:
                                    pass

                                else:
                                    if self.map[cords[0]][cords[1] + i].pos == self.c_node.bridges[1]["connection"]:
                                        # connect
                                        self.s_node = self.map[cords[0]][cords[1] + i]

                                        self.c_node.bridges[1]["bridge_num"] -= 1
                                        self.s_node.bridges[0]["bridge_num"] -= 1

                                        if self.c_node.bridges[1]["bridge_num"] == -1:
                                            self.c_node.bridges[1]["bridge_num"] = 0
                                            self.s_node.bridges[0]["bridge_num"] = 0
                                            break

                                        self.temp_removed[1] = 1

                                        if self.c_node.bridges[1]["bridge_num"] == 0:
                                            self.c_node.bridges[1] = {"bridge_num": 0, "connection": True}
                                            self.s_node.bridges[0] = {"bridge_num": 0, "connection": True}

                                        break
                                    else:
                                        if self.c_node.bridges[1]["connection"] is not None and self.map[cords[0]][cords[1] + i].bridge_occupied == 0:
                                            pass
                                        else:
                                            break
                            else:
                                break
                    else:
                        self.__down(cords)
                else:
                    # here we do in case we go up

                    if self.c_node.bridges[0]["bridge_num"] != 2:
                        for i in range(1, self.size):
                            if cords[1] - i > -1:
                                if self.map[cords[0]][cords[1] - i].locked is False:
                                    pass

                                else:
                                    if self.map[cords[0]][cords[1] - i].pos == self.c_node.bridges[0]["connection"]:
                                        # connect
                                        self.s_node = self.map[cords[0]][cords[1] - i]

                                        self.c_node.bridges[0]["bridge_num"] -= 1
                                        self.s_node.bridges[1]["bridge_num"] -= 1

                                        if self.c_node.bridges[0]["bridge_num"] == -1:
                                            self.c_node.bridges[0]["bridge_num"] -= 1
                                            self.s_node.bridges[1]["bridge_num"] -= 1
                                            break

                                        self.temp_removed[0] = 1

                                        if self.c_node.bridges[0]["bridge_num"] == 0:
                                            self.c_node.bridges[0] = {"bridge_num": 0, "connection": True}
                                            self.s_node.bridges[1] = {"bridge_num": 0, "connection": True}

                                        break
                                    else:
                                        if self.c_node.bridges[0]["connection"] is not None and self.map[cords[0]][cords[1] - i].bridge_occupied == 0:
                                            pass
                                        else:
                                            break
                            else:
                                break
                    else:
                        self.__up(cords)

    def clear_temp(self):
        if self.temp_done.count(1) != 0:
            i = self.temp_done.index(1)
            self.temp_done[i] = 0

            if i == 0:
                self.c_node.bridges[0]["bridge_num"] -= 1
                self.s_node.bridges[1]["bridge_num"] -= 1

                if self.c_node.bridges[0]["bridge_num"] == 0:
                    self.c_node.bridges[0] = {"bridge_num": 0, "connection": None}
                    self.s_node.bridges[1] = {"bridge_num": 0, "connection": None}
                elif self.c_node.bridges[0]["bridge_num"] == -1:
                    self.c_node.bridges[0]["bridge_num"] = 2
                    self.s_node.bridges[1]["bridge_num"] = 2

                    self.c_node.bridges[0]["connection"] = self.s_node.pos
                    self.s_node.bridges[1]["connection"] = self.c_node.pos
            elif i == 1:
                self.c_node.bridges[1]["bridge_num"] -= 1
                self.s_node.bridges[0]["bridge_num"] -= 1

                if self.c_node.bridges[1]["bridge_num"] == 0:
                    self.c_node.bridges[1] = {"bridge_num": 0, "connection": None}
                    self.s_node.bridges[0] = {"bridge_num": 0, "connection": None}
                elif self.c_node.bridges[1]["bridge_num"] == -1:
                    self.c_node.bridges[1]["bridge_num"] = 2
                    self.s_node.bridges[0]["bridge_num"] = 2

                    self.c_node.bridges[1]["connection"] = self.s_node.pos
                    self.s_node.bridges[0]["connection"] = self.c_node.pos
            elif i == 2:
                self.c_node.bridges[2]["bridge_num"] -= 1
                self.s_node.bridges[3]["bridge_num"] -= 1

                if self.c_node.bridges[2]["bridge_num"] == 0:
                    self.c_node.bridges[2] = {"bridge_num": 0, "connection": None}
                    self.s_node.bridges[3] = {"bridge_num": 0, "connection": None}
                elif self.c_node.bridges[2]["bridge_num"] == -1:
                    self.c_node.bridges[2]["bridge_num"] = 2
                    self.s_node.bridges[3]["bridge_num"] = 2

                    self.c_node.bridges[2]["connection"] = self.s_node.pos
                    self.s_node.bridges[3]["connection"] = self.c_node.pos
            elif i == 3:
                self.c_node.bridges[3]["bridge_num"] -= 1
                self.s_node.bridges[2]["bridge_num"] -= 1

                if self.c_node.bridges[3]["bridge_num"] == 0:
                    self.c_node.bridges[3] = {"bridge_num": 0, "connection": None}
                    self.s_node.bridges[2] = {"bridge_num": 0, "connection": None}
                elif self.c_node.bridges[3]["bridge_num"] == -1:
                    self.c_node.bridges[3]["bridge_num"] = 2
                    self.s_node.bridges[2]["bridge_num"] = 2

                    self.c_node.bridges[3]["connection"] = self.s_node.pos
                    self.s_node.bridges[2]["connection"] = self.c_node.pos

    def clear_temp_remove(self):
        if self.temp_removed.count(1) != 0:
            i = self.temp_removed.index(1)
            self.temp_removed[i] = 0
            cords = self.c_node.pos

            if i == 0:
                for i in range(1, self.size):
                    if cords[1] - i > -1:
                        if self.map[cords[0]][cords[1] - i].locked is False:
                            pass

                        else:
                            if self.map[cords[0]][cords[1] - i].pos == self.s_node.pos:
                                # connect
                                self.s_node = self.map[cords[0]][cords[1] - i]

                                self.c_node.bridges[0]["bridge_num"] += 1
                                self.s_node.bridges[1]["bridge_num"] += 1

                                if self.c_node.bridges[0]["bridge_num"] == 3:
                                    self.c_node.bridges[0] = {"bridge_num": 0, "connection": None}
                                    self.s_node.bridges[1] = {"bridge_num": 0, "connection": None}
                                else:
                                    self.c_node.bridges[0]["connection"] = self.s_node.pos
                                    self.s_node.bridges[1]["connection"] = self.c_node.pos

                                break
                            else:
                                if self.c_node.bridges[0]["connection"] is not None and self.map[cords[0]][cords[1] - i].bridge_occupied == 0:
                                    pass
                                else:
                                    break
                    else:
                        break
            elif i == 1:
                for i in range(1, self.size):
                    if cords[1] + i < self.size:
                        if self.map[cords[0]][cords[1] + i].locked is False:
                            pass

                        else:
                            if self.map[cords[0]][cords[1] + i].pos == self.s_node.pos:
                                # connect
                                self.s_node = self.map[cords[0]][cords[1] + i]

                                self.c_node.bridges[1]["bridge_num"] += 1
                                self.s_node.bridges[0]["bridge_num"] += 1

                                if self.c_node.bridges[1]["bridge_num"] == 3:
                                    self.c_node.bridges[1] = {"bridge_num": 0, "connection": None}
                                    self.s_node.bridges[0] = {"bridge_num": 0, "connection": None}
                                else:
                                    self.c_node.bridges[1]["connection"] = self.s_node.pos
                                    self.s_node.bridges[0]["connection"] = self.c_node.pos

                                break
                            else:
                                if self.c_node.bridges[1]["connection"] is not None and self.map[cords[0]][cords[1] + i].bridge_occupied == 0:
                                    pass
                                else:
                                    break
                    else:
                        break
            elif i == 2:
                for i in range(1, self.size):
                    if cords[0] + i < self.size:
                        if self.map[cords[0] + i][cords[1]].locked is False:
                            pass

                        else:
                            if self.map[cords[0] + i][cords[1]].pos == self.s_node.pos:
                                # connect
                                self.s_node = self.map[cords[0] + i][cords[1]]

                                self.c_node.bridges[2]["bridge_num"] += 1
                                self.s_node.bridges[3]["bridge_num"] += 1

                                if self.c_node.bridges[2]["bridge_num"] == 3:
                                    self.c_node.bridges[2] = {"bridge_num": 0, "connection": None}
                                    self.s_node.bridges[3] = {"bridge_num": 0, "connection": None}
                                else:
                                    self.c_node.bridges[2]["connection"] = self.s_node.pos
                                    self.s_node.bridges[3]["connection"] = self.c_node.pos

                                break
                            else:
                                if self.c_node.bridges[2]["connection"] is not None and self.map[cords[0] + i][cords[1]].bridge_occupied == 0:
                                    pass
                                else:
                                    break
                    else:
                        break
            elif i == 3:
                for i in range(1, self.size):
                    if cords[0] - i > -1:
                        if self.map[cords[0] - i][cords[1]].locked is False:
                            pass

                        else:
                            if self.map[cords[0] - i][cords[1]].pos == self.s_node.pos:
                                # connect
                                self.s_node = self.map[cords[0] - i][cords[1]]

                                self.c_node.bridges[3]["bridge_num"] += 1
                                self.s_node.bridges[2]["bridge_num"] += 1

                                if self.c_node.bridges[3]["bridge_num"] == 3:
                                    self.c_node.bridges[3] = {"bridge_num": 0, "connection": None}
                                    self.s_node.bridges[2] = {"bridge_num": 0, "connection": None}
                                else:
                                    self.c_node.bridges[3]["connection"] = self.s_node.pos
                                    self.s_node.bridges[2]["connection"] = self.c_node.pos

                                break
                            else:
                                if self.c_node.bridges[3]["connection"] is not None and self.map[cords[0] - i][cords[1]].bridge_occupied == 0:
                                    pass
                                else:
                                    break
                    else:
                        break

    def click_on_locked(self, mouse, scroll):
        c = self.c_node
        s = self.s_node
        temp_done = copy.copy(self.temp_done)
        temp_removed = copy.copy(self.temp_removed)
        other_removed = self.get_other(temp_removed)
        other_done = self.get_other(temp_done)
        self.clear_temp()
        self.clear_temp_remove()

        if temp_done.count(1) != 0:

            # connecting
            i1 = temp_done.index(1)
            i2 = other_done.index(1)

            switch = {"c": False,
                      "s": False}

            if c.bridge_occupied == c.bridge_num:
                switch["c"] = True
            if s.bridge_occupied == s.bridge_num:
                switch["s"] = True

            c.bridges[i1]["bridge_num"] += 1
            s.bridges[i2]["bridge_num"] += 1
            c.bridge_occupied += 1
            s.bridge_occupied += 1

            c.bridges[i1]["connection"] = s.pos
            s.bridges[i2]["connection"] = c.pos

            if c.bridges[i1]["bridge_num"] > 2:
                c.bridges[i1] = {"bridge_num": 0, "connection": None}
                s.bridges[i2] = {"bridge_num": 0, "connection": None}
                c.bridge_occupied -= 3
                s.bridge_occupied -= 3

                # playing sound
                soundsX["remove"].play()
            else:
                soundsX["join"].play()

            if c.bridge_occupied == c.bridge_num or switch["c"]:
                c.widget.switch(mouse.get_scrolled(scroll))
            if s.bridge_occupied == s.bridge_num or switch["s"]:
                s.widget.switch(mouse.get_scrolled(scroll))

            # locking
            if temp_done[1]:
                for i in range(c.pos[1] + 1, s.pos[1]):
                    if c.bridges[1]["connection"] is not None:
                        self.map[c.pos[0]][i].locked = True
                    else:
                        self.map[c.pos[0]][i].locked = False

            elif temp_done[0]:
                for i in range(s.pos[1] + 1, c.pos[1]):
                    if c.bridges[0]["connection"] is not None:
                        self.map[s.pos[0]][i].locked = True
                    else:
                        self.map[s.pos[0]][i].locked = False

            elif temp_done[2]:
                for i in range(c.pos[0] + 1, s.pos[0]):
                    if c.bridges[2]["connection"] is not None:
                        self.map[i][c.pos[1]].locked = True
                    else:
                        self.map[i][c.pos[1]].locked = False

            elif temp_done[3]:
                for i in range(s.pos[0] + 1, c.pos[0]):
                    if c.bridges[3]["connection"] is not None:
                        self.map[i][s.pos[1]].locked = True
                    else:
                        self.map[i][s.pos[1]].locked = False
        elif temp_removed.count(1) != 0:
            # connecting
            i1 = temp_removed.index(1)
            i2 = other_removed.index(1)

            switch = {"c": False,
                      "s": False}

            if c.bridge_occupied == c.bridge_num:
                switch["c"] = True
            if s.bridge_occupied == s.bridge_num:
                switch["s"] = True

            c.bridges[i1]["bridge_num"] -= 1
            s.bridges[i2]["bridge_num"] -= 1
            c.bridge_occupied -= 1
            s.bridge_occupied -= 1

            c.bridges[i1]["connection"] = s.pos
            s.bridges[i2]["connection"] = c.pos

            if c.bridges[i1]["bridge_num"] == 0:
                c.bridges[i1]["connection"] = None
                s.bridges[i2]["connection"] = None

            if switch["c"]:
                c.widget.switch(mouse.get_scrolled(scroll))
            if switch["s"]:
                s.widget.switch(mouse.get_scrolled(scroll))

            # locking
            if temp_removed[1]:
                for i in range(c.pos[1] + 1, s.pos[1]):
                    if c.bridges[1]["connection"] is not None:
                        self.map[c.pos[0]][i].locked = True
                    else:
                        self.map[c.pos[0]][i].locked = False

            elif temp_removed[0]:
                for i in range(s.pos[1] + 1, c.pos[1]):
                    if c.bridges[0]["connection"] is not None:
                        self.map[s.pos[0]][i].locked = True
                    else:
                        self.map[s.pos[0]][i].locked = False

            elif temp_removed[2]:
                for i in range(c.pos[0] + 1, s.pos[0]):
                    if c.bridges[2]["connection"] is not None:
                        self.map[i][c.pos[1]].locked = True
                    else:
                        self.map[i][c.pos[1]].locked = False

            elif temp_removed[3]:
                for i in range(s.pos[0] + 1, c.pos[0]):
                    if c.bridges[3]["connection"] is not None:
                        self.map[i][s.pos[1]].locked = True
                    else:
                        self.map[i][s.pos[1]].locked = False

            # playing sound
            soundsX["remove"].play()

    def check_win(self):
        node_done_count = 0
        test_node = None
        for line in self.map:
            for item in line:
                if item.bridge_num > 0:
                    if item.bridge_num == item.bridge_occupied:
                        node_done_count += 1
                        test_node = item

        if node_done_count == self.node_count:

            # checking if all connected
            nodes_to_do = [test_node]
            nodes_to_remove = []
            appending = []
            while len(nodes_to_do) != 0:
                # making them done
                for node in nodes_to_do:
                    node.check_for_win = True

                for node in nodes_to_do:
                    for connection in node.bridges:
                        if connection["connection"] is not None:
                            if self.map[connection["connection"][0]][connection["connection"][1]].check_for_win is False:
                                appending.append(self.map[connection["connection"][0]][connection["connection"][1]])
                    nodes_to_remove.append(node)

                for node in appending:
                    nodes_to_do.append(node)
                    appending = []

                for node in nodes_to_remove:
                    nodes_to_do.remove(node)
                    nodes_to_remove = []

            win = True
            for line in self.map:
                for item in line:
                    if item.bridge_num > 0:
                        if item.check_for_win is False:
                            win = False

            if win:
                self.win = True
            else:
                for line in self.map:
                    for item in line:
                        item.check_for_win = False

    def save(self, setup):
        save = {"difficulty": setup["difficulty"]}

        connections = []

        for line in self.map:
            for node in line:
                if node.locked is True:
                    if node.bridge_num != 0:
                        connections.append({"pos": node.pos,
                                            "bridges": node.bridges,
                                            "bridge_occupied": node.bridge_occupied,
                                            "locked": node.locked})
                    else:
                        connections.append({"pos": node.pos,
                                            "locked": node.locked})
        save["connections"] = connections

        with open(f"assets/saves/game_saves/{setup['difficulty']}.json", "w") as f:
            json.dump(save, f, indent=4)

    def print_nodes(self):
        print("_" * 20)

        for line in self.map:
            for item in line:
                if item.bridge_num > 0:
                    print(f"| Node at pos {item.widget.pos}, map pos {item.pos}, bridge_num {item.bridge_num}"
                          f" with {item.bridge_occupied} occupied bridges. |")

        print("_" * 20)

    # technical stuff not used inside class
    def set_size(self):
        if self.size <= 15:
            self.indent = (15 / self.size) * 40

    def get_length(self):
        return self.indent * (self.size - 1)

    def lock(self, args):
        self.locked = True
        self.c_node = args[0]

    # technical stuff used inside class
    def __down(self, cords):
        for i in range(1, self.size):
            if cords[1] + i < self.size:
                if self.map[cords[0]][cords[1] + i].locked is False:
                    pass

                else:
                    if self.map[cords[0]][cords[1] + i].bridge_occupied < self.map[cords[0]][
                        cords[1] + i].bridge_num or (
                            self.c_node.bridges[1]["bridge_num"] == 2 and self.map[cords[0]][cords[1] + i].pos ==
                            self.c_node.bridges[1]["connection"]):
                        # connect
                        self.s_node = self.map[cords[0]][cords[1] + i]

                        self.c_node.bridges[1]["bridge_num"] += 1
                        self.s_node.bridges[0]["bridge_num"] += 1
                        self.temp_done[1] = 1

                        if self.c_node.bridges[1]["bridge_num"] == 3:
                            self.c_node.bridges[1] = {"bridge_num": 0, "connection": None}
                            self.s_node.bridges[0] = {"bridge_num": 0, "connection": None}
                        else:
                            self.c_node.bridges[1]["connection"] = self.s_node.pos
                            self.s_node.bridges[0]["connection"] = self.c_node.pos

                        break
                    else:
                        if self.c_node.bridges[1]["connection"] is not None and self.map[cords[0]][
                            cords[1] + i].bridge_occupied == 0:
                            pass
                        else:
                            break
            else:
                break

    def __up(self, cords):
        for i in range(1, self.size):
            if cords[1] - i > -1:
                if self.map[cords[0]][cords[1] - i].locked is False:
                    pass

                else:
                    if self.map[cords[0]][cords[1] - i].bridge_occupied < self.map[cords[0]][
                        cords[1] - i].bridge_num or (
                            self.c_node.bridges[0]["bridge_num"] == 2 and self.map[cords[0]][cords[1] - i].pos ==
                            self.c_node.bridges[0]["connection"]):
                        # connect
                        self.s_node = self.map[cords[0]][cords[1] - i]

                        self.c_node.bridges[0]["bridge_num"] += 1
                        self.s_node.bridges[1]["bridge_num"] += 1
                        self.temp_done[0] = 1

                        if self.c_node.bridges[0]["bridge_num"] == 3:
                            self.c_node.bridges[0] = {"bridge_num": 0, "connection": None}
                            self.s_node.bridges[1] = {"bridge_num": 0, "connection": None}
                        else:
                            self.c_node.bridges[0]["connection"] = self.s_node.pos
                            self.s_node.bridges[1]["connection"] = self.c_node.pos

                        break
                    else:
                        if self.c_node.bridges[0]["connection"] is not None and self.map[cords[0]][
                            cords[1] - i].bridge_occupied == 0:
                            pass
                        else:
                            break
            else:
                break

    def __right(self, cords):
        for i in range(1, self.size):
            if cords[0] + i < self.size:
                if self.map[cords[0] + i][cords[1]].locked is False:
                    pass

                else:
                    if self.map[cords[0] + i][cords[1]].bridge_occupied < self.map[cords[0] + i][
                        cords[1]].bridge_num or (
                            self.c_node.bridges[2]["bridge_num"] == 2 and self.map[cords[0] + i][cords[1]].pos ==
                            self.c_node.bridges[2]["connection"]):
                        # connect
                        self.s_node = self.map[cords[0] + i][cords[1]]

                        self.c_node.bridges[2]["bridge_num"] += 1
                        self.s_node.bridges[3]["bridge_num"] += 1
                        self.temp_done[2] = 1

                        if self.c_node.bridges[2]["bridge_num"] == 3:
                            self.c_node.bridges[2] = {"bridge_num": 0, "connection": None}
                            self.s_node.bridges[3] = {"bridge_num": 0, "connection": None}
                        else:
                            self.c_node.bridges[2]["connection"] = self.s_node.pos
                            self.s_node.bridges[3]["connection"] = self.c_node.pos

                        break
                    else:
                        if self.c_node.bridges[2]["connection"] is not None and self.map[cords[0] + i][
                            cords[1]].bridge_occupied == 0:
                            pass
                        else:
                            break
            else:
                break

    def __left(self, cords):
        for i in range(1, self.size):
            if cords[0] - i > -1:
                if self.map[cords[0] - i][cords[1]].locked is False:
                    pass

                else:
                    if self.map[cords[0] - i][cords[1]].bridge_occupied < self.map[cords[0] - i][
                        cords[1]].bridge_num or (
                            self.c_node.bridges[3]["bridge_num"] == 2 and self.map[cords[0] - i][cords[1]].pos ==
                            self.c_node.bridges[3]["connection"]):
                        # connect
                        self.s_node = self.map[cords[0] - i][cords[1]]

                        self.c_node.bridges[3]["bridge_num"] += 1
                        self.s_node.bridges[2]["bridge_num"] += 1
                        self.temp_done[3] = 1

                        if self.c_node.bridges[3]["bridge_num"] == 3:
                            self.c_node.bridges[3] = {"bridge_num": 0, "connection": None}
                            self.s_node.bridges[2] = {"bridge_num": 0, "connection": None}
                        else:
                            self.c_node.bridges[3]["connection"] = self.s_node.pos
                            self.s_node.bridges[2]["connection"] = self.c_node.pos

                        break
                    else:
                        if self.c_node.bridges[3]["connection"] is not None and self.map[cords[0] - i][
                            cords[1]].bridge_occupied == 0:
                            pass
                        else:
                            break
            else:
                break

    @staticmethod
    def get_other(temp):
        second = [0, 0, 0, 0]

        if temp[0]:
            second[1] = 1
        elif temp[1]:
            second[0] = 1
        elif temp[2]:
            second[3] = 1
        elif temp[3]:
            second[2] = 1

        return second


class NodeG:

    def __init__(self, pos, bridge_num=0):
        self.pos = pos
        self.bridge_occupied = 0
        self.bridge_num = bridge_num
        self.locked = False
        self.widget = None
        self.check_for_win = False

        self.bridges = [{"bridge_num": 0, "connection": None} for _ in range(4)]  # down, up, right, left
