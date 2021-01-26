# Ant Pathfinding

## Setup

Python 3.9.1

## Outline

The CA will be a NxN (size TBD) grid with non-wrapping borders.
The cells in the CA can have the following properties:
* Empty
* Border
* Food (with quantity)
* Ant (either searching or returning food)
* Nest
* Pheromones (with intensity)

Each tick, these transformations are applied:

* Pheromones will decrease in intensity with a certain amount
* Ants searching for food will randomly move
    * When in range of pheromones, they will move in the direction of the pheromones
    * When on the trail of the pheromones, they will move in the direction of the food
    * When on a food tile, "pick up" food
* Ants carrying food will move in the direction of the nest
    * The ant releases some pheromones each cell moved
    * When they arrive at the nest, they start searching for food again

bars
python food.py --multi --file ex3 ex5 ex6
