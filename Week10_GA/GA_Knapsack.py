from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import random
import numpy
import matplotlib.pyplot as plt
import seaborn as sns
import Knapsack_Rosetta

# create an instance of knapsack problem
knapsack = Knapsack_Rosetta.Knapsack01Problem()

# Genetic Algorithm constants:
POPULATION_SIZE = 50  # The larger the better but large population is more computational expensive
P_CROSSOVER = 0.9
P_MUTATION = 0.1  # set the probability to be small to maintain the stability of evolution
MAX_GENERATIONS = 50  # the number of generations to evolute
HALL_OF_FAME_SIZE = 1  # the size of the best individuals retained to live in the next generation

# set the random seed to reproduce the result
random.seed(42)

toolbox = base.Toolbox()

# create an operator that randomly returns 0 or 1:
toolbox.register("zeroOrOne", random.randint, 0, 1)

# maximise the fitness if set weights to be a positive number
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# create the individual class based on list
creator.create("Individual", list, fitness=creator.FitnessMax)

# create the individual operator to fill up an individual instance
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, len(knapsack))

# create the population operator to generate a list of individuals
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)


def knapsack_value(individual):
    """
    Fitness calculation
    :param individual: a individual from the population
    :return: the fitness
    """
    return knapsack.get_value(individual),


toolbox.register("evaluate", knapsack_value)

# genetic operators:mutFlipBit
# Tournament selection with tournament size of 2. The bigger tournament size will give the population a stronger
# survival pressure to generate a better final solution but it also may lead to a local minima.
toolbox.register("select", tools.selTournament, tournsize=2)

# Use one point crossover
toolbox.register("mate", tools.cxOnePoint)

# Use Flip-bit mutation
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0/len(knapsack))


def main():
    """The framework of this genetic algorithm"""
    # create the first population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics obj to record the data
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", numpy.max)
    stats.register("avg", numpy.mean)

    # The halloffame module provides a way to keep track of the best individuals
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # algorithms.eaSimpl() performs the simplest genetic algorithm in the deap.
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print out the best solution
    best = hof.items[0]
    print("--Best Ever Individual = ", best)
    print("--Best Ever Fitness = ", best.fitness.values[0])
    print("-- Knapsack Items = ")
    knapsack.print_items(best)

    # extract statistics:
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    # plot statistics results
    sns.set_style("whitegrid")
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average fitness over Generations')
    plt.show()


if __name__ == "__main__":
    main()