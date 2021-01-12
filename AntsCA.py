from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice
from copy import deepcopy

class Cell(IntEnum):
    EMPTY = 0,
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4,
    STAY = 5,
    BORDER = 6

INIT_ANT_PROB = .1
BORDER_PHER = -1.
PHER_EVAPORATE = .01

class AntsCA():

    def __init__(self, N=100, neighborhood=VonNeumannNeighborhood()):
        self.N = N
        self.__neighborhood = neighborhood
        self.__grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]


    def __init_cell(self, coords):
        if 0 in coords or self.N-1 in coords:
            return [Cell.BORDER, BORDER_PHER]

        if random() > INIT_ANT_PROB:
            return [Cell.EMPTY, 0.]

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


    def evolve(self):
        self.__sense()
        self.__walk()
    
    def __sense(self):
        # Might be faster to only accumulate edits instead of deepcopying.
        grid_copy = deepcopy(self.__grid)

        for y in range(0, self.N):
            for x in range(0, self.N):
                neighbors = self.__neighborhood.for_coords(x, y, self.N)
                self.__evolve_cell(x, y, neighbors, grid_copy)
        
        self.__grid = grid_copy

    def __evolve_cell(self, x, y, neighbors, grid_copy):
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
        print("x=", x, "y=", y, "nx=", nx, "ny=", ny)
        directions = []
        if nx > x:
            print("Going east.")
            directions.append(Cell.EAST)
        elif nx < x:
            print("Going west.")
            directions.append(Cell.WEST)
        if ny > y:
            print("Going south.")
            directions.append(Cell.SOUTH)
        elif ny < y:
            print("Going north.")
            directions.append(Cell.NORTH)
        
        direction = choice(directions)
        grid_copy[y][x] = [direction, pher]


    def __walk(self):
        pass

if __name__== "__main__":
    N = 5
    ants = AntsCA(N)
    ants.print_grid()
    ants.evolve()
    ants.print_grid()