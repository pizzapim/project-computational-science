from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice
from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors


# Note that for the colormap to work, this list and the bounds list
# must be one larger than the number of different values in the array.
colors_list = ['white', 'brown', 'brown', 'brown', 'brown', 'brown', 'black', 'orange', 'green']
cmap = colors.ListedColormap(colors_list)
bounds = [0,1,2,3,4,5,6,7,8,9]
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
INIT_NEST_PROB = .01
INIT_FOOD_PROB = .01
BORDER_PHER = -1.
PHER_EVAPORATE = .01
MAX_NESTS = 1
MAX_FOOD = 10

class AntsCA():

    def __init__(self, N=100, neighborhood=VonNeumannNeighborhood()):
        self.N = N
        self.NESTS = 0
        self.FOOD = 0
        self.__neighborhood = neighborhood
        self.NEST_COORD = (0,0)
        self.grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]
        self.__init_food()


    def __init_cell(self, coords):

        # Border or Nest
        if 0 in coords or self.N-1 in coords:
            if (random() < INIT_NEST_PROB) and (self.NESTS < MAX_NESTS):
                # Nest not in corner
                if coords not in [(0,0), (0,self.N), (self.N, 0), (self.N, self.N)]:
                    self.NESTS += 1
                    self.NEST_COORD = coords
                    return [Cell.NEST, 0., 0]
            return [Cell.BORDER, BORDER_PHER, 0]

        if random() > INIT_ANT_PROB:
            return [Cell.EMPTY, 0., 0]

        return [Cell(randint(Cell.NORTH, Cell.WEST)), 0., 0]


    def __init_food(self):
        for (x, y) in self.__internal_cells():
            [site, pher, signal] = self.grid[y][x]

            if self.FOOD == MAX_FOOD:
                break
            elif (random() < INIT_FOOD_PROB) and (site in [Cell.NORTH, Cell.WEST, Cell.EAST, Cell.SOUTH]):
                self.FOOD += 1
                self.grid[y][x] = [Cell.FOOD, -2, 0]


    def print_grid(self):
        for y in range(0, self.N):
            for x in range(0, self.N):
                self.print_cell(x, y)
            print()


    def print_cell(self, x, y):
        [state, _, _] = self.grid[y][x]
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
        grid_copy = deepcopy(self.grid)

        for (x, y) in self.__internal_cells():
            neighbors = self.__neighborhood.for_coords(x, y, self.N)
            self.__sense_cell(x, y, neighbors, grid_copy)

        self.grid = grid_copy


    def __sense_cell(self, x, y, neighbors, grid_copy):
        [site, pher, signal] = self.grid[y][x]

        if site in [Cell.BORDER, Cell.EMPTY, Cell.FOOD, Cell.NEST]:
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
            [state, npher, _] = self.grid[ny][nx]
            pher_result = 0.

            if prev == (nx, ny):
                # Do not turn to the cell we just came from.
                pher_result = -2.
            elif state >= Cell.NORTH and state <= Cell.STAY:
                # Do not move to a cell already inhabited.
                pher_result = -2.
            elif state == Cell.FOOD:
                pher_result = -2
                signal = 1
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
            grid_copy[y][x] = [Cell.STAY, pher, signal]
            return

        # We have found a cell, now check how we should turn.
        (nx, ny) = choice(max_cells)
        directions = []
        (cx, cy) = self.NEST_COORD

        if signal == 1:
            if (abs(cx-x) == 0 or abs(cy-y) == 0) and (abs(cx+cy-x-y) == 1):
                if cx > x:
                    directions.append(Cell.EAST)
                elif cx < x:
                    directions.append(Cell.WEST)
                elif cy > y:
                    directions.append(Cell.SOUTH)
                else:
                    directions.append(Cell.NORTH)
                signal = 0
            else:
                if cx > x:
                    directions.append(Cell.EAST)
                elif cx < x:
                    directions.append(Cell.WEST)
                if cy > y:
                    directions.append(Cell.SOUTH)
                elif cy < y:
                    directions.append(Cell.NORTH)
        else:
            if nx > x:
                directions.append(Cell.EAST)
            elif nx < x:
                directions.append(Cell.WEST)
            if ny > y:
                directions.append(Cell.SOUTH)
            elif ny < y:
                directions.append(Cell.NORTH)

        direction = choice(directions)
        grid_copy[y][x] = [direction, pher, signal]


    def __walk(self):
        grid_copy = deepcopy(self.grid)

        for (x, y) in self.__internal_cells():
            self.__walk_cell(x, y, grid_copy)

        self.grid = grid_copy


    def __walk_cell(self, x, y, grid_copy):
        [state, pher, signal] = self.grid[y][x]

        # TODO: reinforce the trail? (rule 10)
        if state == Cell.EMPTY:
            [dstate, _, _] = grid_copy[y][x]
            grid_copy[y][x] = [dstate, max(0., pher-PHER_EVAPORATE), 0]
        elif state == Cell.NORTH:
            [dstate, dpher, _] = grid_copy[y-1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y-1][x] = [Cell.SOUTH, dpher, signal]
            else:
                grid_copy[y][x] = [Cell.STAY, pher, signal]
        elif state == Cell.EAST:
            [dstate, dpher, _] = grid_copy[y][x+1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y][x+1] = [Cell.WEST, dpher, signal]
            else:
                grid_copy[y][x] = [Cell.STAY, pher, signal]
        elif state == Cell.SOUTH:
            [dstate, dpher, _] = grid_copy[y+1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y+1][x] = [Cell.NORTH, dpher, signal]
            else:
                grid_copy[y][x] = [Cell.STAY, pher, signal]
        elif state == Cell.WEST:
            [dstate, dpher, _] = grid_copy[y][x-1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y][x-1] = [Cell.EAST, dpher, signal]
            else:
                grid_copy[y][x] = [Cell.STAY, pher, signal]


def animate(i):
    im.set_data(animate.map)
    ants._AntsCA__sense()
    ants._AntsCA__walk()
    animate.map = [[c[0].value for c in b] for b in ants.grid]


if __name__== "__main__":
    N = 80
    ants = AntsCA(N)
    map = [[c[0].value for c in b] for b in ants.grid]

    fig = plt.figure(figsize=(25/3, 6.25))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(map, cmap=cmap, norm=norm)#, interpolation='nearest')
    animate.map = map

    # Interval between frames (ms).
    interval = 100
    anim = animation.FuncAnimation(fig, animate, interval=interval)
    plt.show()
