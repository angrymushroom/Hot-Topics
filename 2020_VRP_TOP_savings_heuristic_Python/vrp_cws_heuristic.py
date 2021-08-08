""" CLARKE & WRIGHT SAVINGS HEURISTIC FOR THE VEHICLE ROUTING PROBLEM (VRP) """

import random
import time

from routing_objects import Edge, Route, Solution
import math
import operator

""" Read instance data from txt file """


class CWS:

    def __init__(self):
        self.solutions = {}

    def createSL(self, inputs):
        savingsList = []
        for i in range(1, len(inputs.nodes) - 1):  # excludes the depot
            iNode = inputs.nodes[i]
            for j in range(i + 1, len(inputs.nodes)):
                jNode = inputs.nodes[j]
                ijEdge = Edge(iNode, jNode)  # creates the (i, j) edge
                jiEdge = Edge(jNode, iNode)
                ijEdge.invEdge = jiEdge  # sets the inverse edge (arc)
                jiEdge.invEdge = ijEdge
                # compute the Euclidean distance as cost
                # ijEdge.cost = math.sqrt((jNode.x - iNode.x)**2 + (jNode.y - iNode.y)**2)
                ijEdge.cost = inputs.distanceMatrix[jNode.ID][iNode.ID]
                jiEdge.cost = ijEdge.cost  # assume symmetric costs
                # compute savings as proposed by Clark % Wright
                ijEdge.savings = iNode.ndEdge.cost + jNode.dnEdge.cost - ijEdge.cost
                jiEdge.savings = ijEdge.savings
                # save one edge in the savings list
                savingsList.append(ijEdge)
                # sort the list of edges from higher to lower savings
                savingsList.sort(key=operator.attrgetter("savings"), reverse=True)
        return savingsList

    """ Construct the dummy solution """

    def dummySol(self, inputs):
        sol = Solution()
        for node in inputs.nodes[1:]:  # excludes the depot
            dnEdge = node.dnEdge  # get the (depot, node) edge
            ndEdge = node.ndEdge
            dndRoute = Route()  # construct the route (depot, node, depot)
            dndRoute.edges.append(dnEdge)
            dndRoute.demand += node.demand
            dndRoute.cost += dnEdge.cost
            dndRoute.edges.append(ndEdge)
            dndRoute.cost += ndEdge.cost
            node.inRoute = dndRoute  # save in node a reference to its current route
            node.isInterior = False  # this node is currently exterior (connected to depot)
            sol.routes.append(dndRoute)  # add this route to the solution
            sol.cost += dndRoute.cost
            sol.demand += dndRoute.demand
        return sol

    """ Perform the edge-selection & routing-merging iterative process """

    def checkMergingConditions(self, inputs, iNode, jNode, iRoute, jRoute):
        # condition 1: iRoute and jRoure are not the same route object
        if iRoute == jRoute: return False
        # condition 2: both nodes are exterior nodes in their respective routes
        if iNode.isInterior == True or jNode.isInterior == True: return False
        # condition 3: demand after merging can be covered by a single vehicle
        if inputs.vehCap < iRoute.demand + jRoute.demand: return False
        # else, merging is feasible
        return True

    def getRandomPosition(self, beta1, beta2, size):
        # Get a number between beta1 and beta2
        beta = beta1 + random.random() * (beta2 - beta1)

        # Our index is computed as Int(Ln(U) / Ln(1-B))
        # which is a geometrically distributed random number with lambda = -ln(1-B) if U is a uniformly distributed random number in [0,1)
        U = random.random()
        index = int(math.log(U) / math.log(1 - beta))
        # return our index...
        index = index % size
        return index

    def getDepotEdge(self, inputs, aRoute, aNode):
        ''' returns the edge in aRoute that contains aNode and the depot
          (it will be the first or the last one) '''
        # check if first edge in aRoute contains aNode and depot
        origin = aRoute.edges[0].origin
        end = aRoute.edges[0].end
        if ((origin == aNode and end == inputs.depot) or
                (origin == inputs.depot and end == aNode)):
            return aRoute.edges[0]
        else:  # return last edge in aRoute
            return aRoute.edges[-1]

    def CWS(self, inputs, sol, savingsList, beta1, beta2, random):
        while len(savingsList) > 0:  # list is not empty
            pos = 0
            if random:
                pos = self.getRandomPosition(beta1, beta2, len(savingsList))
            ijEdge = savingsList.pop(pos)  # select the next edge from the list
            # determine the nodes i < j that define the edge
            iNode = ijEdge.origin
            jNode = ijEdge.end
            # determine the routes associated with each node
            iRoute = iNode.inRoute
            jRoute = jNode.inRoute
            # check if merge is possible
            isMergeFeasible = self.checkMergingConditions(inputs, iNode, jNode, iRoute, jRoute)
            # if all necessary conditions are satisfied, merge
            if isMergeFeasible == True:
                # iRoute will contain either edge (depot, i) or edge (i, depot)
                iEdge = self.getDepotEdge(inputs, iRoute, iNode)  # iEdge is either (0,i) or (i,0)
                # remove iEdge from iRoute and update iRoute cost
                iRoute.edges.remove(iEdge)
                iRoute.cost -= iEdge.cost
                # if there are multiple edges in iRoute, then i will be interior
                if len(iRoute.edges) > 1: iNode.isInterior = True
                # if new iRoute does not start at 0 it must be reversed
                if iRoute.edges[0].origin != inputs.depot: iRoute.reverse()
                # jRoute will contain either edge (depot, j) or edge (j, depot)
                jEdge = self.getDepotEdge(inputs, jRoute, jNode)  # jEdge is either (0,j) or (j,0)
                # remove jEdge from jRoute and update jRoute cost
                jRoute.edges.remove(jEdge)
                jRoute.cost -= jEdge.cost
                # if there are multiple edges in jRute, then j will be interior
                if len(jRoute.edges) > 1: jNode.isInterior = True
                # if new jRoute starts at 0 it must be reversed
                if jRoute.edges[0].origin == inputs.depot: jRoute.reverse()
                # add ijEdge to iRoute
                iRoute.edges.append(ijEdge)
                iRoute.cost += ijEdge.cost
                iRoute.demand += jNode.demand
                jNode.inRoute = iRoute
                # add jRoute to new iRoute
                for edge in jRoute.edges:
                    iRoute.edges.append(edge)
                    iRoute.cost += edge.cost
                    iRoute.demand += edge.end.demand
                    edge.end.inRoute = iRoute
                # delete jRoute from emerging solution
                sol.cost -= ijEdge.savings
                sol.routes.remove(jRoute)

    def solveCWS(self, inputs, beta1, beta2, random):
        SL = self.createSL(inputs)
        sol = self.dummySol(inputs)
        self.CWS(inputs, sol, SL, beta1, beta2, random)
        return sol

    def multiStart(self, inputs, processingTime, beta1, beta2):
        start = time.time()
        elapsed = 0.0
        bestSol = self.solveCWS(inputs, beta1, beta2, False)  # greedy
        greedySol = bestSol

        while elapsed < processingTime:
            newSol = self.solveCWS(inputs, beta1, beta2, True)  # BR
            elapsed = time.time() - start
            # self.solutions[newSol.ID] = newSol.cost
            if newSol.cost < bestSol.cost:
                bestSol = newSol

        return greedySol, bestSol