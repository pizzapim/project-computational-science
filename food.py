import argparse
import pickle
import matplotlib.pyplot as plt
import numpy as np

from AntsCA import AntsCA, Cell


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


def experiment(filename, n):
    results = {}
    count = 0
    for (sources, amount) in inputs:
        results[(sources, amount)] = []
        for _ in range(n):
            ca = AntsCA(food_sources=sources, food_amount=amount)
            (nestx, nesty) = ca.NEST_COORD
            while True:
                ca.evolve()
                food = ca.grid[nesty][nestx][2]
                if food == sources * amount:
                    break
            food = [i[0] for i in ca.counter]
            on_pher = [i[1] for i in ca.counter]
            results[(sources, amount)].append((food, on_pher))
            count += 1
            print(count)
    
    pickle.dump(results, open(filename, "wb"))
        

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
    parser.add_argument('--graph', action='store_true')
    parser.add_argument('--file', default='food_results.p')
    parser.add_argument('--n', type=int, default=1)
    args = parser.parse_args()

    if not (args.experiment ^ args.graph):
        print("Choose either --experiment or --graph.")
        exit(1)
    
    if args.experiment:
        experiment(args.file, args.n)
    else:
        graph(args.file)