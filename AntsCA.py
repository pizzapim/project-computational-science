from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice
from copy import deepcopy
import argparse

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
INIT_ANT_PROB = .05
INIT_NEST_PROB = .01
INIT_FOOD_PROB = .1
INIT_FOOD_PER_SPOT = 10
BORDER_PHER = -1.
PHER_EVAPORATE = .01
MAX_NESTS = 1
MAX_FOOD = 10


class AntsCA():

    def __init__(self, N=100, neighborhood=VonNeumannNeighborhood(), preset=None):
        self.NESTS = 0
        self.FOOD = 0
        self.__neighborhood = neighborhood
        self.NEST_COORD = (0,0)

        if preset:
            self.load_file(preset)
        else:
            # If no preset is given, initialize the grid randomly.
            self.N = N
            self.grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]
            self.__init_food()


    # Load a file containing a preset grid for debugging and reproducability.
    # Note that the grid must be NxN.
    def load_file(self, preset):
        self.N = None
        with open(preset) as f:
            filecontents = f.readlines()

        self.grid = []
        for y, line in enumerate(filecontents):
            self.grid.append([])
            if not self.N:
                self.N = len(line) - 1

            for x, char in enumerate(line):
                if char == "B":
                    cell = [Cell.BORDER, BORDER_PHER, 0]
                elif char == "E":
                    cell = [Cell.EMPTY, 0., 0]
                elif char == "N":
                    self.NEST_COORD = (x, y)
                    cell = [Cell.NEST, -2, 0]
                elif char == "A":
                    cell = [Cell(randint(Cell.NORTH, Cell.WEST)), 0., 0]
                elif char == "F":
                    cell = [Cell.FOOD, -2, INIT_FOOD_PER_SPOT]
                elif char == "\n":
                    continue
                self.grid[y].append(cell)


    # Initialize each cell in grid to become a border, empty or an ant.
    def __init_cell(self, coords):
        if 0 in coords or self.N-1 in coords:
            return [Cell.BORDER, BORDER_PHER, 0]

        if random() > INIT_ANT_PROB:
            return [Cell.EMPTY, 0., 0]

        return [Cell(randint(Cell.NORTH, Cell.WEST)), 0., 0]


    # Changes some ants to food and nests.
    def __init_food(self):
        for (x, y) in self.__internal_cells():
            [site, _, _] = self.grid[y][x]

            if self.FOOD == MAX_FOOD:
                break
            elif (random() < INIT_FOOD_PROB) and (site in [Cell.NORTH, Cell.WEST, Cell.EAST, Cell.SOUTH]):
                self.FOOD += 1
                self.grid[y][x] = [Cell.FOOD, -2, INIT_FOOD_PER_SPOT]
            elif (random() < INIT_NEST_PROB) and (self.NESTS < MAX_NESTS):
                self.NESTS += 1
                self.NEST_COORD = (x,y)
                self.grid[y][x] = [Cell.NEST, -2, 0]


    # Print grid in text.
    def print_grid(self):
        for y in range(0, self.N):
            for x in range(0, self.N):
                self.print_cell(x, y)
            print()


    # Print cell in text.
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
            printchar("F")


    # Get coordinates of each cell within the borders.
    def __internal_cells(self):
        for y in range(1, self.N-1):
            for x in range(1, self.N-1):
                yield (x, y)


    # Advance the CA one time step.
    def evolve(self):
        self.__sense()
        self.__walk()


    # Execute the "sense" algorithm from the book on the grid,
    # which rotates each ant towards the cell it wants to move to.
    def __sense(self):
        # TODO: Might be faster to only accumulate edits instead of deepcopying.
        grid_copy = deepcopy(self.grid)

        for (x, y) in self.__internal_cells():
            neighbors = self.__neighborhood.for_coords(x, y, self.N)
            self.__sense_cell(x, y, neighbors, grid_copy)

        self.grid = grid_copy


    # Execute the "sense" algorithm from the book for each cell.
    def __sense_cell(self, x, y, neighbors, grid_copy):
        [site, pher, signal] = self.grid[y][x]

        # Skip if the cell does not contain an ant.
        if site < Cell.NORTH or site > Cell.STAY:
            return

        # At this time he ant faces the way it just came from,
        # but can also be STAY if it did not move the last time step.
        prev = None
        if site == Cell.NORTH:
            prev = (x, y-1)
        elif site == Cell.SOUTH:
            prev = (x, y+1)
        elif site == Cell.WEST:
            prev = (x-1, y)
        elif site == Cell.EAST:
            prev = (x+1, y)

        # Determine which directions the ant can turn to.
        directions = []
        (cx, cy) = self.NEST_COORD

        # If the ant has food, it moves to the nest.
        # If next to a nest and carrying food, the ant turns 180 degrees and loses his food.
        if signal == 1:
            if (abs(cx-x) == 0 or abs(cy-y) == 0) and (abs(cx+cy-x-y) == 1):
                if cx > x and self.grid[y][x-1][0] == Cell.EMPTY:
                    directions.append(Cell.WEST)
                elif cx < x and self.grid[y][x-1][0] == Cell.EMPTY:
                    directions.append(Cell.EAST)
                elif cy > y and self.grid[y+1][x][0] == Cell.EMPTY:
                    directions.append(Cell.NORTH)
                elif cy < y and self.grid[y-1][x][0] == Cell.EMPTY:
                    directions.append(Cell.SOUTH)
                signal = 0
            else:
                self.__return_direction(cx, cy, x, y, directions, prev)

        # If the ant is searching for food, it turns to cells with the highest pheromones.
        # If the ant has food but cannot move towards the nest this time step, also do this.
        if signal == 0 or directions == []:
            (best, signal) = self.__find_best_neighbor(neighbors, prev, signal, grid_copy)
            if not best:
                # Could not find a cell to move to, stay in place.
                grid_copy[y][x] = [Cell.STAY, pher, signal]
                return

            (nx, ny) = best
            self.__return_direction(nx, ny, x, y, directions)

        direction = choice(directions)
        grid_copy[y][x] = [direction, pher, signal]


    # Find the neighbor cell with the heighest pheromones to move to.
    # Also update the signal in case the ant is next to the nest.
    def __find_best_neighbor(self, neighbors, prev, signal, grid_copy):
        max_pher = float('-inf')
        max_cells = []

        # Find the cell(s) in the neighborhood with the highest pheromones.
        for (nx, ny) in neighbors:
            [state, npher, nsig] = self.grid[ny][nx]
            pher_result = 0.

            if prev == (nx, ny):
                # Do not turn to the cell we just came from.
                pher_result = -2.
            elif state >= Cell.NORTH and state <= Cell.STAY:
                # Do not move to a cell already inhabited.
                pher_result = -2.
            elif state == Cell.FOOD:
                # If neighbor is food we change signal to 1 to imply an ant with food.
                pher_result = -2.
                if signal == 0:
                    # Take food if ant does not have food already.
                    if (nsig - 1) > 0:
                        grid_copy[ny][nx] = [state, npher, nsig - 1]
                    else:
                        grid_copy[ny][nx] = [Cell.EMPTY, 0, 0]
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
            return (None, signal)

        # We have found a cell, now check how we should turn.
        return (choice(max_cells), signal)


    # Update the directions list with directions the ant can go to
    # in order to reach the given goal.
    def __return_direction(self, nx, ny, x, y, directions, prev=None):
        if nx > x and self.grid[y][x+1][0] == Cell.EMPTY and (x+1, y) != prev:
            directions.append(Cell.EAST)
        elif nx < x and self.grid[y][x-1][0] == Cell.EMPTY and (x-1, y) != prev:
            directions.append(Cell.WEST)
        if ny > y and self.grid[y+1][x][0] == Cell.EMPTY and (x, y+1) != prev:
            directions.append(Cell.SOUTH)
        elif ny < y and self.grid[y-1][x][0] == Cell.EMPTY and (x, y-1) != prev:
            directions.append(Cell.NORTH)


    # Execute the "walk" algorithm from the book for the grid.
    # This moves the ants towards the cell they turned to, if possible.
    # Also update the pheromones for each cell.
    def __walk(self):
        grid_copy = deepcopy(self.grid)

        for (x, y) in self.__internal_cells():
            self.__walk_cell(x, y, grid_copy)

        self.grid = grid_copy


    # Execute the "walk" algorithm from the book for each cell.
    def __walk_cell(self, x, y, grid_copy):
        [state, pher, signal] = self.grid[y][x]

        if state in [Cell.NEST, Cell.FOOD]:
            return

        if state == Cell.EMPTY:
            # If the cell is empty, update its pheromones.
            if grid_copy[y][x][0] == Cell.EMPTY:
                [dstate, _, _] = grid_copy[y][x]
                grid_copy[y][x] = [dstate, max(0., pher-PHER_EVAPORATE), 0]
            return
                
        # For each possible direction, attempt to move the ant there.
        # If not possible, stay in place.
        moved = False
        if state == Cell.NORTH:
            [dstate, dpher, _] = grid_copy[y-1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y-1][x] = [Cell.SOUTH, dpher, signal]
                moved = True
        elif state == Cell.EAST:
            [dstate, dpher, _] = grid_copy[y][x+1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y][x+1] = [Cell.WEST, dpher, signal]
                moved = True
        elif state == Cell.SOUTH:
            [dstate, dpher, _] = grid_copy[y+1][x]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y+1][x] = [Cell.NORTH, dpher, signal]
                moved = True
        elif state == Cell.WEST:
            [dstate, dpher, _] = grid_copy[y][x-1]
            if dstate == Cell.EMPTY:
                grid_copy[y][x] = [Cell.EMPTY, pher, 0]
                grid_copy[y][x-1] = [Cell.EAST, dpher, signal]
                moved = True
                
        if not moved:
            grid_copy[y][x] = [Cell.STAY, pher, signal]


# Advance one time step and draw the CA.
def animate(i):
    im.set_data(animate.map)
    ants.evolve()
    animate.map = [[c[0].value for c in b] for b in ants.grid]


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--preset')
    args = parser.parse_args()

    N = 50
    if args.preset:
        ants = AntsCA(preset=args.preset)
    else:
        ants = AntsCA(N)

    map = [[c[0].value for c in b] for b in ants.grid]

    fig = plt.figure(figsize=(25/3, 6.25))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(map, cmap=cmap, norm=norm)#, interpolation='nearest')
    animate.map = map

    # Interval between frames (ms).
    interval = 50
    anim = animation.FuncAnimation(fig, animate, interval=interval)
    plt.show()
