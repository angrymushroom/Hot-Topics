from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import random
import numpy
import matplotlib.pyplot as plt
import seaborn as sns

ONE_MAX_LENGTH = 100

# Genetic Algorithm constants:
POPULATION_SIZE = 100  # The larger the better but large population is more computational expensive
P_CROSSOVER = 0.9
P_MUTATION = 0.7  # set the probability to be small to maintain the stability of evolution
MAX_GENERATIONS = 50  # the number of generations to evolute
HALL_OF_FAME_SIZE = 5  # the size of the best individuals retained to live in the next generation

# set the random seed to reproduce the result
random.seed(42)


def one_max_fitness(individual):
    """
    Fitness calculation
    :param individual: a individual from the population
    :return: the fitness tuple
    """
    return sum(individual),


toolbox = base.Toolbox()

# create an operator that randomly returns 0 or 1:
toolbox.register("zeroOrOne", random.randint, 0, 1)

# maximise the fitness if set weights to be a positive number
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# create the individual class based on list
creator.create("Individual", list, fitness=creator.FitnessMax)

# create the individual operator to fill up an individual instance
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, ONE_MAX_LENGTH)

# create the population operator to generate a list of individuals
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)


toolbox.register("evaluate", one_max_fitness)

# genetic operators:mutFlipBit
# Tournament selection with tournament size of 2. The bigger tournament size will give the population a stronger
# survival pressure to generate a better final solution but it also may lead to a local minima.
toolbox.register("select", tools.selTournament, tournsize=2)

# Use one point crossover
toolbox.register("mate", tools.cxTwoPoint)

# Use Flip-bit mutation
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0/ONE_MAX_LENGTH)


def main():
    """The flow of this genetic algorithm"""
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
