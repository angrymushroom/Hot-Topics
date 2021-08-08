from algorithms import launch


def main():
    """
    Main function.

    Try different alpha value to test which greedy level is the best.
    """

    experiment_number = 15  # run the experiment 15 times

    temp_cost = []
    # run 30 times to calculate the mean cost of each alpha value
    for i in range(experiment_number):
        best_cost = launch(df='gr96-tsp.txt')
        temp_cost.append(best_cost)
    cost_mean = sum(temp_cost)/len(temp_cost)

    print('Cost: ', cost_mean)


if __name__ == '__main__':
    main()
