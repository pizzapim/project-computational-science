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

        iteration = [i[0] for i in ants.counter]
        food = [i[1] for i in ants.counter]
        on_pher = [i[2] for i in ants.counter]

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
            for j in range(10):
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
            std_len = np.std(it_needed)
            mean_len = np.mean(it_needed)
            it_vals.append(mean_len)
            it_vals_lower.append(mean_len - std_len)
            it_vals_upper.append(mean_len + std_len)

            pher_list = np.asarray([i[1][:min(it_needed)] for i in all_variables]).mean(axis=0)
            all_pher.append(pher_list)

        if not args.no_graphs:
            fig, axs = plt.subplots(ncols=2, figsize=(18,6), sharey=True)

            for p, c in zip(all_pher, ['blue', 'green']):
                axs[0].plot(np.arange(len(p)), p)
                # ax1.fill_between(evap_rate_vals, it_vals_lower, it_vals_upper, alpha=0.2, color=c)
            axs[0].set_title('Median evaporation')
            axs[0].set(xlabel='Iterations', ylabel='Evaporation rate')

            axs[1].plot(evap_rate_vals, it_vals)
            axs[1].fill_between(evap_rate_vals, it_vals_lower, it_vals_upper, alpha=0.2, color="green")
            axs[1].set_title('Median iteration')
            axs[1].set(xlabel='Evaporation rate', ylabel='Iterations')
            plt.show()