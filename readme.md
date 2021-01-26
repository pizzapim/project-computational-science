# Ant Pathfinding

## Setup

Python 3.9.1

## Outline

The CA will be a NxN grid with non-wrapping borders.
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

## Commands used to get our results
<span style="color:orange">**Note: we ran with a n=10 to get the average out of 10 runs, this takes longer to run.**</span> \
ex1: python3 food.py --experiment --file ex1 --n 10 --ants 50 \
ex2: python3 food.py --experiment --file ex2 --n 10 --ants 100 \
ex3: python3 food.py --experiment --file ex3 --n 10 --ants 150 \
\
<span style="color:red">**Warning: This one takes quite a long time to run!**</span> \
ex3d: python3 food.py --experiment3d --file ex3d --n 5 --ants 100

## Commands to plot the results
python3 food.py --graph --file (ex1/ex2/ex3) \
python3 food.py --graph3d --file ex3d
python3 food.py --multi --file ex1 ex2 ex3
