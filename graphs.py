from AntsCA import Cell, AntsCA

import argparse
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from matplotlib import cm

import numpy as np


# Really hacky but mixing qualitative & quantitative color maps is annoying.
viridis = cm.get_cmap('Greys', 100)
newcolors = viridis(np.linspace(0, 1, 100))
newcolors[0:5] = [0.00,1.00,0.16,1]
newcolors[6:55] = [0.60,0.20,0.00,1]
newcolors[56:65] = [0,0,0,1]
newcolors[66:75] = [1.00,1.00,0.10,1]
newcolors[76:100] = viridis(np.linspace(0, 1, 48)[0:24])
newcmp = colors.ListedColormap(newcolors)

# Advance one time step and draw the CA.
def animate(i):
    im.set_data(animate.map)
    ants.evolve()
    animate.map = [[c[0].value / 10. + (c[1]/5. if c[0] == Cell.EMPTY else 0) for c in b] for b in ants.grid]

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

def graph_ants_evap_iterate(all_pher):
    plt.figure(figsize=(15,5))
    for p in all_pher:
        plt.plot(np.arange(len(p)), p)
    plt.xlabel('Iterations')
    plt.ylabel('Ants on pheromone trail')
    plt.title('Mean of ants on pheromone trail per iteration')
    plt.show()

def graphs_iteration_per_evap(it_needed):
    std_len = np.std(it_needed)
    mean_len = np.mean(it_needed)
    it_vals.append(mean_len)
    it_vals_lower.append(mean_len - std_len)
    it_vals_upper.append(mean_len + std_len)

    plt.figure(figsize=(15,5))

    plt.plot(evap_rate_vals, it_vals)
    plt.fill_between(evap_rate_vals, it_vals_lower, it_vals_upper, alpha=0.2, color="green")
    plt.title('Mean iteration per evaporation rate')
    plt.xlabel('Evaporation rate')
    plt.ylabel('Iterations')
    plt.show()

def graphs_iteration_per_evap_diff(it_needed):
    std_len = np.std(it_needed)
    mean_len = np.mean(it_needed)
    it_vals.append(mean_len)
    it_vals_lower.append(mean_len - std_len)
    it_vals_upper.append(mean_len + std_len)

    plt.figure(figsize=(15,5))

    plt.plot(evap_rate_vals, it_vals)
    plt.fill_between(evap_rate_vals, it_vals_lower, it_vals_upper, alpha=0.2, color="green")
    plt.title('Mean iteration per evaporation rate')
    plt.xlabel('Evaporation rate')
    plt.ylabel('Iterations')
    plt.show()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--preset')
    parser.add_argument('--no-graphs', action='store_true')
    parser.add_argument('--animate', action='store_true')
    args = parser.parse_args()

    N = 50
    if args.preset:
        ants = AntsCA(preset=args.preset)
    else:
        ants = AntsCA(N)

    if args.animate:
        mapping = [[c[0].value / 10. + (c[1]/5. if c[0] == Cell.EMPTY else 0) for c in b] for b in ants.grid]

        fig = plt.figure(figsize=(25/3, 6.25))
        ax = fig.add_subplot(111)
        ax.set_axis_off()
        im = ax.imshow(mapping, cmap=newcmp, vmin=0, vmax=1)#, interpolation='nearest')
        animate.map = mapping

        # Interval between frames (ms).
        interval = 1
        anim = animation.FuncAnimation(fig, animate, interval=interval)
        plt.show()

        food = [i[1] for i in ants.counter]
        on_pher = [i[2] for i in ants.counter]
        iteration = [i for i in range(len(on_pher))]

        if not args.no_graphs:
            graph_food_time(iteration, food)
            graph_on_pher_time(iteration, on_pher)

    else:
        all_variables = []
        all_pher = []
        it_vals = []
        it_vals_lower = []
        it_vals_upper = []
        # if we want to look at the mean of food or something we need to change range to higher.
        evap_rate_vals = np.linspace(0.001, 0.0099, 2)

        for e in evap_rate_vals:
            for j in range(3):
                ants = AntsCA(N)
                ants.PHER_EVAPORATE = e
                while True:
                    ants.evolve()
                    (cx, cy) = ants.NEST_COORD
                    food = ants.grid[cy][cx][2]
                    if food == ants.INIT_FOOD_PER_SPOT * ants.INIT_N_FOOD:
                        break

                food = [i[0] for i in ants.counter]
                on_pher = [i[1] for i in ants.counter]

                all_variables.append([food, on_pher])
                print('#################')
                print(j)
                print('#################')

            it_needed = [len(i[1]) for i in all_variables]

            pher_list = np.asarray([i[1][:min(it_needed)] for i in all_variables]).mean(axis=0)
            all_pher.append(pher_list)

        if not args.no_graphs:
            graph_ants_evap_iterate(all_pher)
            graphs_iteration_per_evap(it_needed)