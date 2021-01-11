from enum import IntEnum
from random import random, randint

class Cell(IntEnum):
    EMPTY = 0,
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4,
    STAY = 5,
    BORDER = 6
    
INIT_ANT_PROB = .001
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