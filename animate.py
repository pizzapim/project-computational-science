from AntsCA import Cell, AntsCA

import numpy as np
import argparse
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from matplotlib import cm



# Really hacky but mixing qualitative & quantitative color maps is annoying.
viridis = cm.get_cmap('Greys', 100)
newcolors = viridis(np.linspace(0, 1, 100))
newcolors[0:5] = [0.00,1.00,0.16,1]
newcolors[6:55] = [0.60,0.20,0.00,1]
newcolors[56:65] = [0,0,0,1]
newcolors[66:75] = [1.00,1.00,0.10,1]
newcolors[76:100] = viridis(np.linspace(0, 1, 48)[0:24])
newcmp = colors.ListedColormap(newcolors)

# Advance one time step and draw the CA using a mapping.
def animate(i):
    im.set_data(animate.map)
    ants.evolve()
    animate.map = [[c[0].value / 10. + (c[1]/5. if c[0] == Cell.EMPTY else 0) for c in b] for b in ants.grid]

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--preset')
    args = parser.parse_args()

    # Choose preset or no preset.
    if args.preset:
        ants = AntsCA(preset=args.preset)
    else:
        ants = AntsCA()

    # implement the first color mapping of the grid.
    mapping = [[c[0].value / 10. + (c[1]/5. if c[0] == Cell.EMPTY else 0) for c in b] for b in ants.grid]

    # Plot animation.
    fig = plt.figure(figsize=(25/3, 6.25))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(mapping, cmap=newcmp, vmin=0, vmax=1)#, interpolation='nearest')
    animate.map = mapping

    # Interval between frames (ms).
    interval = 1
    anim = animation.FuncAnimation(fig, animate, interval=interval)
    plt.show()
