from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice
from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors


# Colours for visualization: brown for EMPTY, dark green for TREE and orange
# for FIRE. Note that for the colormap to work, this list and the bounds list
# must be one larger than the number of different values in the array.
colors_list = ['white', 'brown', 'purple', 'yellow', 'green', 'brown', 'black', 'grey', 'yellow']
cmap = colors.ListedColormap(colors_list)
bounds = [0,1,2,3,4,5,6,7,8]
norm = colors.BoundaryNorm(bounds, cmap.N)

class Cell(IntEnum):
    EMPTY = 0,
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4,
    STAY = 5,
    BORDER = 6,
    NEST = 7,
    FOOD = 8

# Configuration variables
INIT_ANT_PROB = .1
BORDER_PHER = -1.
PHER_EVAPORATE = .01
INIT_NEST_PROB = .1
MAX_NESTS = 1
MAX_FOOD = 10

class AntsCA():

    def __init__(self, N=100, neighborhood=VonNeumannNeighborhood()):
        self.N = N
        self.NESTS = 0
        self.FOOD = 0
        self.__neighborhood = neighborhood
        self.__grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]



    def __init_cell(self, coords):

        # Border or Nest
        if 0 in coords or self.N-1 in coords:
            # if random() < INIT_NEST_PROB and self.NESTS < MAX_NESTS:
            #     # Nest not in corner
            #     if coords not in [(0,0), (0,self.N), (self.N, 0), (self.N, self.N)]:
            #         self.NESTS += 1
            #         return [Cell.NEST, 0.]
            return [Cell.BORDER, BORDER_PHER]

        if random() > INIT_ANT_PROB:
            return [Cell.EMPTY, 0.]

        # if self.FOOD < MAX_FOOD:
        #     self.FOOD += 1
        #     return [Cell.FOOD, 0.]

        return [Cell(randint(Cell.NORTH, Cell.WEST)), 0.]


    def print_grid(self):
        for y in range(0, self.N):
            for x in range(0, self.N):
                self.print_cell(x, y)
            print()


    def print_cell(self, x, y):
        [state, _] = self.__grid[y][x]
        printchar = lambda s: print(s, end="")

        if state == Cell.BORDER:
            printchar("B")
        elif state == Cell.EMPTY:
            printchar(" ")
        elif state == Cell.NORTH:
            printchar("↑")
        elif state == Cell.EAST:
            printchar("→")
        elif state == Cell.SOUTH:
            printchar("↓")
        elif state == Cell.WEST:
            printchar("←")
        elif state == Cell.STAY:
            printchar("·")
        elif state == Cell.NEST:
            printchar("N")
        elif state == Cell.FOOD:
            printchar("A")


    def __internal_cells(self):
        for y in range(1, self.N-1):
            for x in range(1, self.N-1):
                yield (x, y)


    def evolve(self):
        self.__sense()
        self.__walk()


    def __sense(self):
        # Might be faster to only accumulate edits instead of deepcopying.
        grid_copy = deepcopy(self.__grid)

        for (x, y) in self.__internal_cells():
            neighbors = self.__neighborhood.for_coords(x, y, self.N)
            self.__sense_cell(x, y, neighbors, grid_copy)

        self.__grid = grid_copy


    def __sense_cell(self, x, y, neighbors, grid_copy):
        [site, pher] = self.__grid[y][x]

        if site in [Cell.BORDER, Cell.EMPTY]:
            return

        # The ant faces the way it just came from, but can also be STAY.
        prev = None
        if site == Cell.NORTH:
            prev = (x, y-1)
        elif site == Cell.SOUTH:
            prev = (x, y+1)
        elif site == Cell.WEST:
            prev = (x-1, y)
        elif site == Cell.EAST:
            prev = (x+1, y)

        max_pher = float('-inf')
        max_cells = []

        # Find the cell(s) in the neighborhood with the highest pheromones.
        for (nx, ny) in neighbors:
            [state, npher] = self.__grid[ny][nx]
            pher_result = 0.

            if prev == (nx, ny):
                # Do not turn to the cell we just came from.
                pher_result = -2.
            elif state >= Cell.NORTH and state <= Cell.STAY:
                # Do not move to a cell already inhabited.
                pher_result = -2.
            # elif state == Cell.FOOD:
            # elif state == Cell.NEST:
            else:
                pher_result = npher

            if pher_result > max_pher:
                # We have seen a cell with higher pheromones.
                max_pher = pher_result
                max_cells = [(nx, ny)]
            elif pher_result == max_pher:
                # We have seen a cell with equal pheromones.
                max_cells.append((nx, ny))

        if max_pher < 0.:
            # Can't see a cell with positive pheromones, stay in place.
            grid_copy[y][x] = [Cell.STAY, pher]
            return

        # We have found a cell, now check how we should turn.
        (nx, ny) = choice(max_cells)
        directions = []
        if nx > x:
            directions.append(Cell.EAST)
        elif nx < x:
            directions.append(Cell.WEST)
        if ny > y:
            directions.append(Cell.SOUTH)
        elif ny < y:
            directions.append(Cell.NORTH)

        direction = choice(directions)
        grid_copy[y][x] = [direction, pher]


    def __walk(self):
        grid_copy = deepcopy(self.__grid)

        for (x, y) in self.__internal_cells():
            grid_copy = self.__walk_cell(x, y, grid_copy)

        self.__grid = grid_copy


    def __walk_cell(self, x, y, grid_copy):
        [state, pher] = self.__grid[y][x]

        # TODO: reinforce the trail? (rule 10)
        if state == Cell.EMPTY:
            [dstate, _] = grid_copy[y][x]
            grid_copy[y][x] = [dstate, max(0., pher-PHER_EVAPORATE)]
        elif state == Cell.NORTH:
            [dstate, dpher] = grid_copy[y-1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher]
                grid_copy[y-1][x] = [Cell.SOUTH, dpher]
            else:
                grid_copy[y][x] = [Cell.STAY, pher]
        elif state == Cell.EAST:
            [dstate, dpher] = grid_copy[y][x+1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher]
                grid_copy[y][x+1] = [Cell.WEST, dpher]
            else:
                grid_copy[y][x] = [Cell.STAY, pher]
        elif state == Cell.SOUTH:
            [dstate, dpher] = grid_copy[y+1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher]
                grid_copy[y+1][x] = [Cell.NORTH, dpher]
            else:
                grid_copy[y][x] = [Cell.STAY, pher]
        elif state == Cell.WEST:
            [dstate, dpher] = grid_copy[y][x-1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher]
                grid_copy[y][x-1] = [Cell.EAST, dpher]
            else:
                grid_copy[y][x] = [Cell.STAY, pher]


if __name__== "__main__":
    N = 20
    ants = AntsCA(N)
    X = [[c[0].value for c in b] for b in ants.__grid]

    fig = plt.figure(figsize=(25/3, 6.25))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(X, cmap=cmap, norm=norm)#, interpolation='nearest')
    # The animation function: called to produce a frame for each generation.
    def animate(i):
        im.set_data(animate.X)
        ants._AntsCA__sense()
        print([[c[0].value for c in b] for b in ants.__grid][1])
        animate.X = [[c[0].value for c in b] for b in ants.__grid]
    # Bind our grid to the identifier X in the animate function's namespace.
    animate.X = X

    # Interval between frames (ms).
    interval = 100
    anim = animation.FuncAnimation(fig, animate, interval=interval)
    plt.show()
