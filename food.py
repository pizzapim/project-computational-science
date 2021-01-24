import argparse
import pickle

from AntsCA import AntsCA, Cell

# Pairs of number of food sources & amount of food per source.
# All add up to 12 food.
# This number is a superior highly composite number,
# which means we will be able to divide it in lots of ways.
# TBD: we can also try 60, but might be to many sources.
inputs = [
    (1, 12),
    (2, 6),
    (3, 4),
    (4, 3),
    (6, 2),
    (12, 1)
]


def experiment(filename, n):
    results = {}
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
    
    pickle.dump(results, open(filename, "wb"))
        

def graph(filename):
    # Structure of results is a dictionary with keys (number of sources, amount per source)
    # and value a list with each run.
    # Each list item contains (food per iteration, ants on pheromones trail)
    results = pickle.load(open(filename, "rb"))


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