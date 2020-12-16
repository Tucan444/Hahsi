import random


class Hashi:

    def __init__(self, size):
        if size < 2:
            size = 2
            print("Size cant be 1 or lower.")
        self.size = size
        self.node_limit_lower = size  # lower limit
        self.node_upper_limit = int(size ** 1.4) + 1  # upper limit
        self.node_count = 0
        self.low_lim = 0
        self.high_lim = size

        self.map = [[Node([x, y]) for y in range(size)] for x in range(size)]

    def generate_map(self):
        # down, up, right, left
        first = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
        self.node_count += 1

        node = self.get_node(first)
        self.write_node(node)
        nodes_to_do = self.get_new_nodes(node)
        while len(nodes_to_do) != 0:
            for n in nodes_to_do:
                node = self.get_node(n)
                self.write_node(node)
                nodes_to_do = nodes_to_do + self.get_new_nodes(node)
                nodes_to_do.remove(n)

    def get_node(self, cords):
        ways = [0, 0, 0, 0]  # down, up, right, left
        possibilities = 0

        if self.node_count >= self.node_upper_limit:
            node = {"ways": [0, 0, 0, 0],
                    "num_of_bridges": [random.randint(1, 2) for _ in range(4)],
                    "pos": cords}

            return node

        if cords[1] - 1 > -1 and self.map[cords[0]][cords[1] - 1].locked is False:
            ways[0] += 1
            possibilities += 1

        if cords[1] + 1 < self.size and self.map[cords[0]][cords[1] + 1].locked is False:
            ways[1] += 1
            possibilities += 1

        if cords[0] + 1 < self.size and self.map[cords[0] + 1][cords[1]].locked is False:
            ways[2] += 1
            possibilities += 1

        if cords[0] - 1 > -1 and self.map[cords[0] - 1][cords[1]].locked is False:
            ways[3] += 1
            possibilities += 1

        if possibilities:
            attempts = [x+1 if random.randint(0, 1) == 0 else x for x in ways]

            # making the puzzle forcefully bigger
            if self.node_count < self.node_limit_lower:
                while 2 not in attempts:
                    attempts = [x + 1 if random.randint(0, 1) == 0 else x for x in ways]

            # getting the starting distances
            distances = [1 if x > 1 else 0 for x in attempts]

            # getting possible distance up to 6
            if attempts[0] > 1:
                for i in range(2, self.size):
                    if cords[1] - i > -1 and self.map[cords[0]][cords[1] - i].locked is False:
                        distances[0] += 1
                    else:
                        break

            if attempts[1] > 1:
                for i in range(2, self.size):
                    if cords[1]+i < self.size and self.map[cords[0]][cords[1]+i].locked is False:
                        distances[1] += 1
                    else:
                        break

            if attempts[2] > 1:
                for i in range(2, self.size):
                    if cords[0] + i < self.size and self.map[cords[0]+i][cords[1]].locked is False:
                        distances[2] += 1
                    else:
                        break

            if attempts[3] > 1:
                for i in range(2, self.size):
                    if cords[0] - i > -1 and self.map[cords[0] - i][cords[1]].locked is False:
                        distances[3] += 1
                    else:
                        break

            final_decision = [random.randint(1, x)if x != 0 else 0 for x in distances]

            node = {"ways": final_decision,
                    "num_of_bridges": [random.randint(1, 2) for _ in range(4)],
                    "pos": cords}

            return node

        else:
            node = {"ways": [0, 0, 0, 0],
                    "num_of_bridges": [random.randint(1, 2) for _ in range(4)],
                    "pos": cords}

            return node

    def write_node(self, node):
        pos = node["pos"]

        i = 0
        sum_of_bridges = 0
        for item in node["ways"]:
            if item != 0:
                sum_of_bridges += node["num_of_bridges"][i]

                # adding the bridges to new nodes
                if i == 0:
                    self.map[pos[0]][pos[1] - item].bridge_num += node["num_of_bridges"][i]
                elif i == 1:
                    self.map[pos[0]][pos[1] + item].bridge_num += node["num_of_bridges"][i]
                elif i == 2:
                    self.map[pos[0] + item][pos[1]].bridge_num += node["num_of_bridges"][i]
                elif i == 3:
                    self.map[pos[0] - item][pos[1]].bridge_num += node["num_of_bridges"][i]

            i += 1

        self.map[pos[0]][pos[1]].locked = True
        self.map[pos[0]][pos[1]].bridge_num += sum_of_bridges

    def get_new_nodes(self, node):
        pos = node["pos"]
        # down, up, right, left
        nodes_to_send = []

        for nodeX in range(1, node["ways"][0]+1):
            self.map[pos[0]][pos[1] - nodeX].locked = True

            if nodeX == node["ways"][0]:
                nodes_to_send.append(self.map[pos[0]][pos[1] - nodeX].pos)

        for nodeX in range(1, node["ways"][1]+1):
            self.map[pos[0]][pos[1] + nodeX].locked = True

            if nodeX == node["ways"][1]:
                nodes_to_send.append(self.map[pos[0]][pos[1] + nodeX].pos)

        for nodeX in range(1, node["ways"][2]+1):
            self.map[pos[0] + nodeX][pos[1]].locked = True

            if nodeX == node["ways"][2]:
                nodes_to_send.append(self.map[pos[0] + nodeX][pos[1]].pos)

        for nodeX in range(1, node["ways"][3]+1):
            self.map[pos[0] - nodeX][pos[1]].locked = True

            if nodeX == node["ways"][3]:
                nodes_to_send.append(self.map[pos[0] - nodeX][pos[1]].pos)

        self.node_count += len(nodes_to_send)

        return nodes_to_send

    def save(self, path):
        final_string = ""

        for y in range(self.size):

            for x in range(self.size):
                final_string += str(self.map[x][y].bridge_num) + " "

            final_string += "\n"

        with open(path, "w") as f:
            f.write(final_string)
            f.close()

    def print(self, bridges=False):
        final_string = "_" * ((self.size * 2) + 3) + "\n"

        for y in range(self.size):
            final_string += "| "

            for x in range(self.size):
                if bridges is False:
                    final_string += str(self.map[x][y].bridge_num) + " "
                else:
                    final_string += f" |* {self.map[x][y].bridge_num} *,{str(self.map[x][y].locked)[0]}| "

            final_string += "|\n"

        final_string += "¯" * ((self.size * 2) + 3)

        print(final_string)

    def __len__(self):
        return self.node_count

    def __str__(self):
        final_string = "_" * ((self.size*2)+3) + "\n"

        for y in range(self.size):
            final_string += "| "

            for x in range(self.size):
                final_string += str(self.map[x][y].bridge_num) + " "

            final_string += "|\n"

        final_string += "¯" * ((self.size*2)+3)

        return final_string

    def __add__(self, other):
        return self.node_count + other.node_count


class Node:

    def __init__(self, pos, bridge_num=0):
        self.pos = pos
        self.bridge_num = bridge_num
        self.locked = False
