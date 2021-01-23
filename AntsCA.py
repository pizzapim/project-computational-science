from Neighborhood import VonNeumannNeighborhood

from enum import IntEnum
from random import random, randint, choice, randrange
from copy import deepcopy


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


class AntsCA():
    # Configuration variables
    BORDER_PHER = -1.
    FOOD_PHER = -2
    PHER_EVAPORATE = .005
    INIT_ANT_SIGNAL = 100
    INIT_FOOD_PER_SPOT = 10
    INIT_N_FOOD = 10

    def __init__(self, N=100, ants_count=100, neighborhood=VonNeumannNeighborhood(), preset=None):
        self.FOOD_IN_NEST = 0
        self.__neighborhood = neighborhood
        self.NEST_COORD = (0,0)
        self.counter = [[0,0]]
        self.ants_count = ants_count

        if preset:
            self.load_file(preset)
        else:
            # If no preset is given, initialize the grid randomly.
            self.N = N
            self.grid = [[self.__init_cell((x, y)) for x in range(0, N)] for y in range(0, N)]
            self.__populate_grid()


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
                    cell = [Cell.BORDER, self.BORDER_PHER, 0]
                elif char == "E":
                    cell = [Cell.EMPTY, 0., 0]
                elif char == "N":
                    self.NEST_COORD = (x, y)
                    cell = [Cell.NEST, -2, 0]
                elif char == "A":
                    cell = [Cell(randint(Cell.NORTH, Cell.WEST)), 0., 0]
                elif char == "F":
                    cell = [Cell.FOOD, self.FOOD_PHER, self.INIT_FOOD_PER_SPOT]
                elif char == "\n":
                    continue
                self.grid[y].append(cell)


    # Initialize each cell in grid the grid to become border or empty.
    def __init_cell(self, coords):
        if 0 in coords or self.N-1 in coords:
            return [Cell.BORDER, self.BORDER_PHER, 0]

        return [Cell.EMPTY, 0., 0]


    # Initializing the nest, food cells and ants.
    def __populate_grid(self):
        x = int(self.N / 2)
        y = 2
        self.grid[y][x] = [Cell.NEST, -2, 0]
        self.NEST_COORD = (x,y)

        # Randomly place food cells.
        n_food = 0
        while n_food < self.INIT_N_FOOD:
            x = randrange(1, self.N - 1)
            y = randrange(1, self.N - 1)

            if self.grid[y][x][0] == Cell.EMPTY:
                self.grid[y][x] = [Cell.FOOD, self.FOOD_PHER, self.INIT_FOOD_PER_SPOT]
                n_food += 1

        n_ants = 0
        while n_ants < self.ants_count:
            x = randrange(1, self.N - 1)
            y = randrange(1, self.N - 1)

            if self.grid[y][x][0] == Cell.EMPTY:
                cell = Cell(randint(Cell.NORTH, Cell.WEST))
                self.grid[y][x] = [cell, 0., 0]
                n_ants += 1

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
        self.__count()

    # Execute the "sense" algorithm from the book on the grid,
    # which rotates each ant towards the cell it wants to move to.
    def __sense(self):
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
        if signal > 0:
            if (abs(cx-x) == 0 or abs(cy-y) == 0) and (abs(cx+cy-x-y) == 1):
                # Increment the signal in the nest, indicating food collected.
                grid_copy[cy][cx][2] += 1
                if cx > x and self.grid[y][x-1][0] == Cell.EMPTY:
                    directions.append(Cell.WEST)
                elif cx < x and self.grid[y][x-1][0] == Cell.EMPTY:
                    directions.append(Cell.EAST)
                elif cy > y and self.grid[y+1][x][0] == Cell.EMPTY:
                    directions.append(Cell.NORTH)
                elif cy < y and self.grid[y-1][x][0] == Cell.EMPTY:
                    directions.append(Cell.SOUTH)

                signal = 0
                print(grid_copy[cy][cx][2])
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
                # If neighbor is food we set the signal to imply an ant with food.
                pher_result = -2.
                if signal == 0:
                    # Take food if ant does not have food already.
                    if (nsig - 1) > 0:
                        self.grid[ny][nx][2] -= 1
                        grid_copy[ny][nx] = [state, npher, nsig - 1]
                    else:
                        grid_copy[ny][nx] = [Cell.EMPTY, 0, 0]
                    signal = self.INIT_ANT_SIGNAL
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
                grid_copy[y][x] = [dstate, max(0., pher- self.PHER_EVAPORATE), 0]
            return

        # For each possible direction, attempt to move the ant there.
        # If not possible, stay in place.
        dx = dy = direction = dpher = None
        moved = False
        if state == Cell.NORTH:
            [dstate, dpher, _] = grid_copy[y-1][x]
            if dstate == Cell.EMPTY:
                dx = x
                dy = y-1
                direction = Cell.SOUTH
                moved = True
        elif state == Cell.EAST:
            [dstate, dpher, _] = grid_copy[y][x+1]
            if dstate == Cell.EMPTY:
                dx = x+1
                dy = y
                direction = Cell.WEST
                moved = True
        elif state == Cell.SOUTH:
            [dstate, dpher, _] = grid_copy[y+1][x]
            if dstate == Cell.EMPTY:
                dx = x
                dy = y+1
                direction = Cell.NORTH
                moved = True
        elif state == Cell.WEST:
            [dstate, dpher, _] = grid_copy[y][x-1]
            if dstate == Cell.EMPTY:
                dx = x-1
                dy = y
                direction = Cell.EAST
                moved = True

        if moved:
            move_pher = dpher if signal <= 0 else signal / self.INIT_ANT_SIGNAL
            signal = signal if signal <= 1 else signal-1

            grid_copy[y][x] = [Cell.EMPTY, move_pher, 0]
            grid_copy[dy][dx] = [direction, dpher, signal]
        else:
            grid_copy[y][x] = [Cell.STAY, pher, signal]

    # Count variables of AntsCA for graphs.
    def __count(self):

        (cx, cy) = self.NEST_COORD
        food = self.grid[cy][cx][2]

        # Should be incorperated in sense to reduce computation.
        on_pher = 0
        for (x, y) in self.__internal_cells():
            [site, pher, _] = self.grid[y][x]
            if site >= Cell.NORTH and site <= Cell.STAY and pher > 0:
                on_pher += 1

        self.counter.append([food, on_pher])