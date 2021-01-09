#!/usr/bin/env python3

from cellular_automaton import CellularAutomaton, RadialNeighborhood, CAWindow, EdgeRule

class AntsCA(CellularAutomaton):
    
    def __init__(self):
        super().__init__(dimension=[100, 100], # Dimensions TBD
                         neighborhood=RadialNeighborhood(EdgeRule.IGNORE_EDGE_CELLS, radius=2)) # Radius will be dynamic
    
    def init_cell_state(self, __):
       return [0.] # Replace with real initial cell state
    
    def evolve_rule(self, last_cell_state, neighbors_last_states):
        return [1. - last_cell_state[0]]

if __name__ == "__main__":
    CAWindow(cellular_automaton=AntsCA(),
                window_size=(1000, 830)).run(evolutions_per_second=1)