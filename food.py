import argparse
import pickle
import matplotlib.pyplot as plt
import numpy as np

from AntsCA import AntsCA, Cell

from mpl_toolkits import mplot3d

# Pairs of number of food sources & amount of food per source.
# All add up to 12 food.
# This number is a superior highly composite number,
# which means we will be able to divide it in lots of ways.
# TBD: we can also try 60, but might be to many sources.
inputs = [
    (1, 180),
    (2, 90),
    (3, 60),
    (6, 30),
    (9, 20),
    (12, 15),
    (15, 12),
    (20, 9),
    (30, 6),
    (60, 3),
    (90, 2),
    (180, 1)
]

def experiment3d(filename, n):
    src = np.arange(10, 110, 10)
    amt = np.arange(10, 110, 10)
    srcv, amtv = np.meshgrid(src, amt)
    meanIts = np.copy(srcv)
    count = 1

    print("Points to calc: " + str(len(src) * len(amt)))

    for i in range(len(src)):
        for j in range(len(amt)):
            print()
            print("Point nr: " + str(count))
            it_it = []
            for time in range(n):
                print("n: " + str(time + 1))
                ca = AntsCA(food_sources=src[i], food_amount=amt[j])
                (nestx, nesty) = ca.NEST_COORD

                while True:
                    ca.evolve()
                    food = ca.grid[nesty][nestx][2]
                    if food >= src[i] * amt[j]:
                        break
                it_it.append(len(ca.counter))
            count += 1

            meanIts[j][i] = int(np.mean(it_it))

    pickle.dump((srcv, amtv, meanIts), open(filename, "wb"))


def experiment(filename, n):
    results = {}
    count = 0
    for (sources, amount) in inputs:
        results[(sources, amount)] = []
        for _ in range(n):
            ca = AntsCA(food_sources=sources, food_amount=amount, ants_count=50)
            (nestx, nesty) = ca.NEST_COORD
            while True:
                ca.evolve()
                food = ca.grid[nesty][nestx][2]
                if food >= sources * amount:
                    break
            food = [i[0] for i in ca.counter]
            on_pher = [i[1] for i in ca.counter]
            results[(sources, amount)].append((food, on_pher))
            count += 1
            print(count)

    pickle.dump(results, open(filename, "wb"))

def graph3d(filename):
    X, Y, Z = pickle.load(open(filename, "rb"))

    plt.figure(figsize=(8,5))
    ax = plt.axes(projection ='3d')
    ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green')
    plt.show()

    cs = plt.contourf(X, Y, Z) 
    cbar = plt.colorbar(cs) 
    plt.title('Number of iterations needed to collect all food') 
    plt.xlabel=('Number of food per foodcell')
    plt.ylabel=('Number of foodcells per simulation')
    plt.show() 


def graph(filename):
    # Structure of results is a dictionary with keys (number of sources, amount per source)
    # and value a list with each run.
    # Each list item contains (food per iteration, ants on pheromones trail)
    results = pickle.load(open(filename, "rb"))
    plt.figure(figsize=(15,5))
    for key, value in results.items():
        plt.plot(np.arange(len(value[0][0])), value[0][0], label=key)
    plt.xlabel('Iterations')
    plt.ylabel('Food')
    plt.title('Food distribution')
    plt.legend()
    plt.show()

    # Bar plot
    plt.figure(figsize=(15,5))
    means = []
    stds = []
    food = []
    keys = []
    for key, value in results.items():
        food.append([i[0] for i in value])
        keys.append(key)
        means.append(np.mean([len(i[0]) for i in value]))
        stds.append(np.std([len(i[0]) for i in value]))

    plt.bar(list(map(str,keys)), means, yerr=stds, align="center", label=key)
    plt.xlabel('Iterations')
    plt.ylabel('Food')
    plt.title('Food collection time for')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', action='store_true')
    parser.add_argument('--experiment3d', action='store_true')
    parser.add_argument('--graph', action='store_true')
    parser.add_argument('--graph3d', action='store_true')
    parser.add_argument('--file', default='food_results.p')
    parser.add_argument('--n', type=int, default=1)
    args = parser.parse_args()

    if not (args.experiment ^ args.graph ^ args.experiment3d ^ args.graph3d):
        print("Choose either --experiment(3d) or --graph(3d).")
        exit(1)

    if args.experiment:
        experiment(args.file, args.n)
    elif args.experiment3d:
        experiment3d(args.file, args.n)
    elif args.graph:
        graph(args.file)
    else:
        graph3d(args.file)