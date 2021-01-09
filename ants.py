#!/usr/bin/env python3

from enum import IntEnum
from random import random, randint, choice

from cellular_automaton import CellularAutomaton, VonNeumannNeighborhood, CAWindow, EdgeRule

class Cell(IntEnum):
    EMPTY = 0,
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4,
    STAY = 5,
    BORDER = 6
    
INIT_ANT_PROB = .001

class AntsCA(CellularAutomaton):
    
    def __init__(self, N=100):
        self.N = N

        # Use Von Neumann neighborhood like in the book, radius wil be dynamic later
        super().__init__(dimension=[N, N],
                         neighborhood=VonNeumannNeighborhood(EdgeRule.IGNORE_MISSING_NEIGHBORS_OF_EDGE_CELLS, radius=1))

    
    # Initialize a cell state; called for each cell
    def init_cell_state(self, coords):
        # Initialize as a border cell
        if 0 in coords or self.N-1 in coords:
            return [Cell.BORDER, -1.]

        # Initialize with no ant
        if random() > INIT_ANT_PROB:
            return [Cell.EMPTY, 0.]
        
        # Initialize with an ant and random direction
        return [Cell(randint(Cell.NORTH, Cell.WEST)), 0.]

    
    def evolve_rule(self, last_cell_state, neighbors_last_states):
        (cell, _) = last_cell_state
        
        # Turn the ants
        if cell != Cell.EMPTY and cell != Cell.BORDER:
            self.sense(last_cell_state, neighbors_last_states)

        return last_cell_state

    
    # Turn the ants in the CA; see page 453 of the book
    def sense(self, last_cell_state, neighbors_last_states):
        max_pher = float('-inf')
        max_cells = []

        # TODO: not sure how to implement rule 2 yet
        for (i, (cell, cell_pher)) in enumerate(neighbors_last_states):
            # If the cell already contains an ant, set pheromones to -2
            if cell != Cell.EMPTY and cell != Cell.BORDER:
                pher = -2.
            else:
                pher = cell_pher
            
            # Find new max pheromones cell or add to list
            if pher > max_pher:
                max_pher = pher
                max_cells = [i]
            elif pher == max_pher:
                max_cells.append(i)
        
        if max_pher < 0.:
            return Cell.STAY
        
        rand_i = choice(max_cells)
        # TODO: we will need to turn to the direction of the cell,
        # but we have no information about coordinates from the library...
        

    @staticmethod
    def state_to_color(state):
        (cell, _) = state
        
        if cell == Cell.EMPTY:
            return 0, 0, 0
        if cell == Cell.BORDER:
            return 255, 0, 0
        return 81, 21, 21


if __name__ == "__main__":
    CAWindow(cellular_automaton=AntsCA(), window_size=(1000, 830),
             state_to_color_cb=AntsCA.state_to_color).run(evolutions_per_second=1)