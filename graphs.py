from AntsCA import Cell, AntsCA

import argparse
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors

import numpy as np


# Note that for the colormap to work, this list and the bounds list
# must be one larger than the number of different values in the array.
colors_list = ['white', 'brown', 'brown', 'brown', 'brown', 'brown', 'black', 'orange', 'green']
cmap = colors.ListedColormap(colors_list)
bounds = [0,1,2,3,4,5,6,7,8,9]
norm = colors.BoundaryNorm(bounds, cmap.N)

# Advance one time step and draw the CA.
def animate(i):
    im.set_data(animate.map)
    ants.evolve()
    animate.map = [[c[0].value for c in b] for b in ants.grid]

def graph_food_time(iteration, food):
    # Plot the amount of food over iterations.
    plt.figure(figsize=(15,5))
    plt.plot(iteration, food)

    # Add labels to the plots.
    plt.ylabel("Amount of food in the nest.")
    plt.xlabel("Iteration")
    plt.title("Amount of food in nest over time.")
    plt.show()

def graph_on_pher_time(iteration, on_pher):
    # Plot the amount of food over iterations.
    plt.figure(figsize=(15,5))
    plt.plot(iteration, on_pher)

    # Add labels to the plots.
    plt.ylabel("Amount of ants on a pheromone trail.")
    plt.xlabel("Iteration")
    plt.title("Amount of ants on a pheromone trail over time.")
    plt.show()

if __name__== "__main__":
    ani = True

    parser = argparse.ArgumentParser()
    parser.add_argument('--preset')
    args = parser.parse_args()

    N = 50
    if args.preset:
        ants = AntsCA(preset=args.preset)
    else:
        ants = AntsCA(N)

    # geanimeerd
    if ani:
        mapping = [[c[0].value for c in b] for b in ants.grid]

        fig = plt.figure(figsize=(25/3, 6.25))
        ax = fig.add_subplot(111)
        ax.set_axis_off()
        im = ax.imshow(mapping, cmap=cmap, norm=norm)#, interpolation='nearest')
        animate.map = mapping

        # Interval between frames (ms).
        interval = 50
        anim = animation.FuncAnimation(fig, animate, interval=interval)
        plt.show()
    else:
        all_variables = []
        # if we want to look at the mean of food or something we need to change range to higher.
        for i in range(1):
            ants = AntsCA(N)
            print('hoi')
            while True:
                ants.evolve()
                (cx, cy) = ants.NEST_COORD
                food = ants.grid[cy][cx][2]
                if food == ants.INIT_FOOD_PER_SPOT * ants.INIT_N_FOOD:
                    break

            iteration = [i[0] for i in ants.counter]
            food = [i[1] for i in ants.counter]
            on_pher = [i[2] for i in ants.counter]

            np.array(all_variables.append([iteration, food, on_pher]))
    
        mean_food = np.asarray([i[1] for i in all_variables]).mean(axis=0)
        mean_pher = np.asarray([i[2] for i in all_variables]).mean(axis=0)

        graph_food_time(iteration, mean_food)
        graph_on_pher_time(iteration, mean_pher)
