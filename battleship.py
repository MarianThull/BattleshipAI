from __future__ import division
__author__ = 'marian'

import copy
import random
import numpy as np
import matplotlib.pyplot as plt


class Battleship:
    WATER = 0
    HIT = 1
    SUNKEN = 2
    WON = 3

    def __init__(self, size, ships=[], random=True):
        self.size = size
        self.positions = []
        self.single_ships = []
        self.ships = ships
        self.shoot_count = 0
        if random:
            self.gen_random_positions()

    def gen_random_positions(self):
        forbidden = [(i, -1) for i in range(self.size)] + [(i, self.size) for i in range(self.size)] + \
                    [(-1, j) for j in range(self.size)] + [(self.size, j) for j in range(self.size)]
        for ship in self.ships:
            horizontal = random.randint(0, 1)
            legal = False
            while not legal:
                if horizontal:
                    row = random.randint(0, 9)
                    left = random.randint(0, self.size - ship)
                    s = [(row, j) for j in range(left, left + ship)]
                else:
                    column = random.randint(0, 9)
                    top = random.randint(0, self.size - ship)
                    s = [(i, column) for i in range(top, top + ship)]

                legal = True
                for pos in s:
                    if pos in forbidden:
                        legal = False
                        break
            if horizontal:
                for i in range(row - 1, row + 2):
                    for j in range(left - 1, left + ship + 1):
                        forbidden.append((i, j))
            else:
                for i in range(top - 1, top + ship + 1):
                    for j in range(column -1, column + 2):
                        forbidden.append((i, j))

            self.positions += s
            self.single_ships.append(s)

    def print_field(self):
        f = np.zeros((self.size, self.size))
        for i, j in self.positions:
            f[i][j] = 1
        print f

    def shoot(self, i, j):
        self.shoot_count += 1
        if (i, j) not in self.positions:
            return Battleship.WATER
        for ship in self.single_ships:
            if (i, j) in ship:
                ship.remove((i, j))
                if len(ship) == 0:
                    self.single_ships.remove(ship)
                    if len(self.single_ships) == 0:
                        return Battleship.WON
                    return Battleship.SUNKEN
                return Battleship.HIT


class BattleshipAI:
    def __init__(self, size, ships, game):
        self.size = size
        self.ships = ships
        self.game = game
        self.shots = []

        self.sunken = []
        self.hits = []

        self.heat_matrix = np.zeros((size, size))
        self.feel_the_heat()

    def feel_the_heat(self):
        # reset heat_matrix
        self.heat_matrix = np.zeros((self.size, self.size))
        # place every ship in all positions
        for ship in self.ships:
            # iterate over rows
            for i in range(self.size):
                # check all horizontal positions
                for j_left in range(0, self.size - ship + 1):
                    js = range(j_left, j_left + ship)
                    # if there is a shot at one of the squares it is not a legal position
                    legal = True
                    for j in js:
                        if (i, j) in self.shots:
                            legal = False
                    if legal:
                        for j in js:
                            self.heat_matrix[i][j] += 1

            # iterate over columns
            for j in range(self.size):
                # check all vertical positions
                for i_top in range(0, self.size - ship + 1):
                    i_s = range(i_top, i_top + ship)
                    # if there is a shot at one of the squares it is not a legal position
                    legal = True
                    for i in i_s:
                        if (i, j) in self.shots:
                            legal = False
                    if legal:
                        for i in i_s:
                            self.heat_matrix[i][j] += 1

    def local_heat_check(self):
        rows = list(set([hit[0] for hit in self.hits]))
        columns = list(set([hit[1] for hit in self.hits]))

        # reset heat_matrix
        self.heat_matrix = np.zeros((self.size, self.size))

        # place every ship in all positions
        for ship in self.ships:
            # if horizontal or unknown check row
            if len(rows) == 1:
                i = rows[0]
                # check all horizontal positions
                for j_left in range(0, self.size - ship + 1):
                    js = range(j_left, j_left + ship)
                    # if there is a shot at one of the squares it is not a legal position
                    legal = True
                    for j in js:
                        if (i, j) in self.shots:
                            legal = False
                    if legal:
                        for j in js:
                            if min(columns) - j == 1 or j - max(columns) == 1:
                                self.heat_matrix[i][j] += 1

            # iterate over columns
            if len(columns) == 1:
                j = columns[0]
                # check all vertical positions
                for i_top in range(0, self.size - ship + 1):
                    i_s = range(i_top, i_top + ship)
                    # if there is a shot at one of the squares it is not a legal position
                    legal = True
                    for i in i_s:
                        if (i, j) in self.shots:
                            legal = False
                    if legal:
                        for i in i_s:
                            if min(rows) - i == 1 or i - max(rows) == 1:
                                self.heat_matrix[i][j] += 1

    def hot_shot(self):
        a = np.argmax(self.heat_matrix)
        j = a % self.size
        i = int((a - j) / self.size)

        v = self.game.shoot(i, j)
        if v == Battleship.HIT:
            self.hits.append((i, j))
            self.sunken.append((i, j))
        elif v == Battleship.SUNKEN:
            self.hits.append((i, j))
            rows = [h[0] for h in self.hits]
            columns = [h[1] for h in self.hits]
            for k in range(min(rows) - 1, max(rows) + 2):
                for l in range(min(columns) - 1, max(columns) + 2):
                    self.shots.append((k, l))
            self.hits = []
            self.sunken.append((i, j))
        elif v == Battleship.WON:
            self.shots += self.hits
            self.sunken.append((i, j))
        else:
            self.shots.append((i, j))

        if len(self.hits) > 0:
            self.local_heat_check()
        else:
            self.feel_the_heat()

        return self.heat_matrix, copy.deepcopy(self.sunken)


def plot_heat(states, cmap, vmin, vmax):
    subplts = np.ceil(np.sqrt(len(states)))
    subx = int(1.7 * subplts)
    suby = np.ceil(len(states) / subx)
    for i in range(len(states)):
        heat_m, sunken = states[i]
        for k, l in sunken:
            heat_m[k][l] = -1

        plt.subplot(suby, subx, i + 1, aspect=1)
        n = plt.pcolor(heat_m, cmap=cmap, vmin=vmin, vmax=vmax, edgecolor='k')
        n.axes.set_ylim(0, heat_m.shape[1])
        n.axes.set_xlim(0, heat_m.shape[0])


if __name__ == '__main__':
    size = 12
    ships = [5, 4, 3, 3, 2]

    game = Battleship(size, ships, True)
    ai = BattleshipAI(size, ships, game)

    vmin = 0
    vmax = ai.heat_matrix.max()
    custom_cmap = plt.cm.hot
    custom_cmap.set_under('b')

    states = []
    count = 0
    while True:
        count += 1
        state = ai.hot_shot()
        # print 'Shot {}. {} fields hit.'.format(count, len(state[1]))
        states.append(state)
        if len(state[1]) == sum(ships) or count == 100:
            break

    print 'Won with {} shots.'.format(count)
    plot_heat(states, custom_cmap, vmin, vmax)
    plt.show()