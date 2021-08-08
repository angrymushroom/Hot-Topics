import pandas as pd
from math import pow, sqrt
import random


def launch(df='bier127-tsp.txt', max_iteration=1000, max_localsearch_iteration=40):
    """
    The frame of this tabu search algorithm

    :param df: a txt file contains the coordinate of nodes
    :param max_iteration: the max number of iterations
    :param max_localsearch_iteration: the max number of solutions generated from one initial solution
    :return: No return value
    """
    input_tsp_file = read_data(df)
    max_iteration = max_iteration
    max_localsearch_iteration = max_localsearch_iteration

    best_sol = {'permutation': construct_initial_solution(input_tsp_file),
                'edges': None
                }
    best_sol['cost'] = tour_cost(best_sol['permutation'])
    print('best solution cost in dict', best_sol['cost'])
    base_sol = best_sol
    credit = 0
    tabu_list = []
    max_tabu_length = 20
    k = 5
    current_iteration = 1
    while max_iteration > 0:
        print('ITERATION %d' % current_iteration)
        current_iteration += 1
        max_iteration -= 1
        new_sols = []
        # use one base solution to generate some local solutions
        for i in range(max_localsearch_iteration):
            new_sol = local_search(base_sol, best_sol, tabu_list)
            new_sols.append(new_sol)

        # select the best solution from the local solutions
        best_new_sol = identify_best_sol(new_sols)

        # set up the criterion if accept a new solution to be the best solution
        difference = best_new_sol['cost'] - base_sol['cost']
        # if best new solution is better than base solution(difference < 0),
        # set it to be the next initial solution (base solution)
        if difference < 0:
            credit = -1*difference
            base_sol = best_new_sol
            # if best new solution is better than the best solution,
            # set it to be the best solution
            if best_new_sol['cost'] < best_sol['cost']:
                best_sol = best_new_sol
                print('Cost: %.2f' % best_sol['cost'])

                # add the switched edges into the tabu list
                for edge in best_sol['edges']:
                    tabu_list.append(edge)

                    # if the length of tabu list is too long, remove the first element of tabu list
                    if len(tabu_list) > max_tabu_length:
                        tabu_list.pop(0)

        # if the best new solution is not better than the best solution but it is not too bad,
        # set it to be the next initial solution (base solution)
        else:
            if difference <= k*credit:
                credit = 0
                base_sol = best_new_sol

    print('The final solution cost: ', best_sol['cost'])

    return best_sol['cost']


def construct_initial_solution(nodes):
    """
    Randomly initialize a solution by switching the position of nodes.
    :param nodes: a list of nodes
    :return: a list of nodes with a new order
    """
    permutation = nodes[:]  # make a copy
    size = len(permutation)

    for index in range(size):
        shuffle_index = random.randrange(index, size)
        permutation[index], permutation[shuffle_index] = permutation[shuffle_index], permutation[index]

    return permutation


def local_search(base_sol, best_sol, tabu_list):
    """
    Generate a new solution that does not contains any edge in the tabu list.
    :param base_sol: the initial solution of a local search
    :param best_sol: the current best solution
    :param tabu_list: the current tabu list
    :return:
    """
    new_permutation, edges, new_sol = None, None, {}
    # generate a new solution better than the
    while new_permutation is None or if_in_tabu(new_permutation, tabu_list):
        new_permutation, edges = stochastic_swap(base_sol['permutation'])
        new_cost = tour_cost(new_permutation)
        if new_cost < best_sol['cost']:
            break

    new_sol['permutation'] = new_permutation
    new_sol['cost'] = new_cost
    new_sol['edges'] = edges

    return new_sol


def identify_best_sol(sols):
    """
    Return the best solution among a list of solutions
    :param sols: a list contains solutions from a local search
    :return: the best solution of these solutions
    """
    sols.sort(key=lambda c: c['cost'])  # sort
    best_sol = sols[0]  # select the best one

    return best_sol


def tour_cost(sol):
    """
    Calculate the euclidean distance of a solution by sum the distance of every distance between each two nodes
    :param sol: a solution made up of a series of nodes
    :return: total distance of a route
    """

    total_distance = 0

    for index in range(len(sol)):
        start_node = sol[index]
        if index == len(sol) - 1:
            end_node = sol[0]
        else:
            end_node = sol[index + 1]

        total_distance += distance(start_node, end_node)

    return total_distance


def distance(node_1, node_2):
    """
    Calculate the euclidean distance between two nodes.
    :param node_1: a node
    :param node_2: another node
    :return: distance between two nodes
    """

    distance_two_nodes = 0

    for x, y in zip(node_1, node_2):
        distance_two_nodes += sqrt(pow((x-y), 2))
    return distance_two_nodes


def stochastic_swap(sol):
    """
    Swap two edges in the route.
    Randomly select two nodes which are different and non-consecutive. Swap the edges between these two nodes
    then reverse the route between them.

    :param sol: a solution made up of a series of nodes
    :return: a new solution
    """

    sol_copy = sol[:]  # create a copy
    sol_size = len(sol)

    node_1_index = random.randrange(0, sol_size)  # randomly select a node
    node_2_index = random.randrange(0, sol_size)  # randomly select another node

    exclude_set = {node_1_index}  # create a forbidden set to guarantee node 2 is not node 1 or the neighbor of node1

    #  the rules exclude set
    if node_1_index == 0:
        exclude_set.add(sol_size-1)
    else:
        exclude_set.add(node_1_index-1)

    if node_1_index == sol_size - 1:
        exclude_set.add(0)
    else:
        exclude_set.add(node_1_index+1)

    #  if the selected node 2 is in the exclude set, select again
    while node_2_index in exclude_set:
        node_2_index = random.randrange(0, sol_size)

    #  to guarantee that node 1 index < node 2 index
    if node_2_index < node_1_index:
        node_1_index, node_2_index = node_2_index, node_1_index

    #  reversed the route between two selected nodes
    sol_copy[node_1_index: node_2_index] = reversed(sol_copy[node_1_index:node_2_index])

    # Return the new permutation and two edges are changed
    return sol_copy, [[sol[node_1_index-1], sol[node_1_index]], [sol[node_2_index-1], sol[node_2_index]]]


def if_in_tabu(permutation, tabu_list):
    """
    Check if any edge is in the tabu list.
    :param permutation: a solution
    :param tabu_list: a tabu list
    :return: True if any edge is in the tabu list
    """
    if_tabu = False

    for index in range(len(permutation)):
        index_start = index
        if index_start == len(permutation) - 1:
            index_end = 0
        else:
            index_end = index_start + 1

        if [permutation[index_start], permutation[index_end]] in tabu_list:
            if_tabu = True

        return if_tabu


def read_data(df):
    """
    Read a txt data file.
    :return: a list of the data file
    """
    df = df

    f = pd.read_csv(df, sep='\s+')
    f = pd.DataFrame(f).to_numpy().tolist()
    return f
