from vrp_cws_heuristic import CWS
from Inputs import Inputs
import sys
import os


def laucher():
    testFile = "tests" + os.sep + "tests2run.txt"
    instances = Inputs.readTestsToRun(testFile)

    for instance in instances:
        # get the data related to the test (i.e., the instance file, the beta value and the number of runs)
        instanceData, beta1, beta2, vehCap, runTime = Inputs.getInstanceParameters(instance)

        if instanceData == None:
            sys.exit("Error, fix instanceData in tests2Run and run again.")

        inputs = Inputs(vehCap, instanceData)
        solutionsFile = 'outputs' + os.sep + 'solution_' + instanceData + '.txt'

        inputs.readInputs()

        cws = CWS()
        greedySol, brSol = cws.multiStart(inputs, runTime, beta1, beta2)
        print('greedySol', "{:.{}f}".format(greedySol.cost, 2))
        greedySol.printSol()
        print('\n\nbrSol', "{:.{}f}".format(brSol.cost, 2))
        brSol.printSol()


        with open(solutionsFile, 'w') as outFile:
            outFile.write('\nGREEDY SOL: \n' + greedySol.str() + '\n\nBR SOL: \n' + brSol.str())
            print('\n\ncomplete solutions are written in "' + solutionsFile + '"')

    # # Plot the solution
    #
    # # G = nx.Graph()
    # # for route in sol.routes:
    # #    for edge in route.edges:
    # #        G.add_edge(edge.origin.ID, edge.end.ID)
    # #        G.add_node(edge.end.ID, coord=(edge.end.x, edge.end.y))
    # # coord = nx.get_node_attributes(G, 'coord')
    # # nx.draw_networkx(G, coord)
    #
    # # Plot (enhanced) the solution
    #
    # def plot(sol):
    #     G = nx.Graph()
    #     fnode = sol.routes[0].edges[0].origin
    #     G.add_node(fnode.ID, coord=(fnode.x, fnode.y))
    #     coord = nx.get_node_attributes(G, 'coord')
    #     fig, ax = plt.subplots()  # Add axes
    #     nx.draw_networkx_nodes(G, coord, node_size=60, node_color='white', ax=ax)
    #     nx.draw_networkx_labels(G, coord)
    #
    #     j = 0
    #     for route in sol.routes:
    #         # Assign random colors in RGB
    #         c1 = int(random.uniform(0, 255)) if (j % 3 == 2) else (j % 3) * int(random.uniform(0, 255))
    #         c2 = int(random.uniform(0, 255)) if ((j + 1) % 3 == 2) else ((j + 1) % 3) * int(random.uniform(0, 255))
    #         c3 = int(random.uniform(0, 255)) if ((j + 2) % 3 == 2) else ((j + 2) % 3) * int(random.uniform(0, 255))
    #         for edge in route.edges:
    #             G.add_edge(edge.origin.ID, edge.end.ID)
    #             G.add_node(edge.end.ID, coord=(edge.end.x, edge.end.y))
    #             coord = nx.get_node_attributes(G, 'coord')
    #             nx.draw_networkx_nodes(G, coord, node_size=60, node_color='white', ax=ax)
    #             nx.draw_networkx_edges(G, coord, edge_color='#%02x%02x%02x' % (c1, c2, c3))
    #             nx.draw_networkx_labels(G, coord, font_size=9)
    #             G.remove_node(edge.origin.ID)
    #         j += 1
    #
    #     limits = plt.axis('on')  # Turn on axes
    #     ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)


if __name__ == "__main__": laucher()
