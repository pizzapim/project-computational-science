#!/usr/bin/env python3

from cellular_automaton import CellularAutomaton, RadialNeighborhood, CAWindow, EdgeRule

class AntsCA(CellularAutomaton):
    
    def __init__(self):
        # TODO: increasing radius seems to crash the library
        super().__init__(dimension=[100, 100], # Dimensions TBD
                         neighborhood=RadialNeighborhood(EdgeRule.IGNORE_MISSING_NEIGHBORS_OF_EDGE_CELLS, radius=1)) # Radius will be dynamic
    
    def init_cell_state(self, __):
       return [0.] # Replace with real initial cell state
    
    def evolve_rule(self, last_cell_state, neighbors_last_states):
        return last_cell_state

if __name__ == "__main__":
    CAWindow(cellular_automaton=AntsCA(),
                window_size=(1000, 830)).run(evolutions_per_second=40)