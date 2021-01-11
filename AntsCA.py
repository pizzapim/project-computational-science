from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice

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

class AntsCA():

    def __init__(self, N=100, neighborhood=VonNeumannNeighborhood()):
        self.N = N
        self.__neighborhood = neighborhood
        self.__grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]


    def __init_cell(self, coords):
        if 0 in coords or self.N-1 in coords:
            return (Cell.BORDER, BORDER_PHER)

        if random() > INIT_ANT_PROB:
            return (Cell.EMPTY, 0.)

        return (Cell(randint(Cell.NORTH, Cell.WEST)), 0.)


    def print_grid(self):
        for y in range(0, self.N):
            for x in range(0, self.N):
                self.print_cell(x, y)
            print()


    def print_cell(self, x, y):
        (state, pher) = self.__grid[x][y]
        printchar = lambda s: print(s, end="")

        if state == Cell.BORDER:
            printchar("B")
        elif state == Cell.EMPTY:
            printchar(" ")
        elif state >= Cell.NORTH and state <= Cell.WEST:
            printchar("A")


    def evolve(self):
        for y in range(1, self.N-1):
            for x in range(1, self.N-1):
                neighbors =  self.__neighborhood.for_coords(x, y, self.N)
                self.__evolve_cell(x, y, neighbors)


    def __evolve_cell(self, x, y, neighbors):
        neigborCells = []
        neigborCells.append(self.__grid[x][y-1])
        neigborCells.append(self.__grid[x+1][y])
        neigborCells.append(self.__grid[x][y+1])
        neigborCells.append(self.__grid[x-1][y])

        (site, pher) = self.__grid[x][y]

        if site != Cell.BORDER and site != Cell.EMPTY:
            if site != Cell.STAY:
                if site == Cell.NORTH:
                    list(neigborCells[0])[1] = -2.
                    tuple(neigborCells[0])
                elif site == Cell.EAST:
                    list(neigborCells[1])[1] = -2.
                    tuple(neigborCells[0])
                elif site == Cell.SOUTH:
                    list(neigborCells[2])[1] = -2.
                    tuple(neigborCells[0])
                elif site == Cell.WEST:
                    list(neigborCells[3])[1] = -2.
                    tuple(neigborCells[0])

            for neigh in neigborCells:
                if neigh[0] != Cell.BORDER and neigh[0] != Cell.EMPTY:
                    list(neigh)[1] = -2.
                    tuple(neigh)

            max_pher = float('-inf')
            max_cells = []

            for i in range(len(neigborCells)-1):
                if neigborCells[i][1] > max_pher:
                    max_pher = neigborCells[i][1]
                    max_cells = [i]
                elif neigborCells[i][1] == max_pher:
                    max_cells.append(i)

            if max_pher < 0.:
                self.__grid[x][y] = (Cell.STAY, pher)
            else:
                rand_i = choice(max_cells) + 1
                self.__grid[x][y] = (rand_i, pher)


if __name__== "__main__":
    N = 10
    ants = AntsCA(N)
    ants.print_grid()
    ants.evolve()
    ants.print_grid()