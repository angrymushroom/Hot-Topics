from routing_objects import Node, Edge


class Inputs:
    """ Read instance data from txt file """

    def __init__(self, vehCap, instanceName):
        self.nNodes = 0
        self.vehCap = vehCap  # update vehicle capacity for each instance
        self.instanceName = instanceName  # name of the instance
        # txt file with the VRP instance data for each node (x, y, demand)
        self.distanceMatrix = []
        self.fileName = 'data/' + self.instanceName + '_input_nodes.txt'
        self.nodes = []
        self.depot = 0

    def readInputs(self):
        with open(self.fileName) as instance:
            i = 0
            for line in instance:
                # array data with node data: x, y, demand
                data = [float(x) for x in line.split(',')[1:]]
                if i == 0:
                    self.nNodes = len(data) - 1

                hospitalName = line.split(',')[0]
                self.distanceMatrix.append(data[:self.nNodes])
                demand = data[self.nNodes]
                aNode = Node(i, 0, 0, demand, hospitalName)
                self.nodes.append(aNode)
                i += 1

        """ Construct edges with costs and savings list from nodes """
        self.depot = self.nodes[0]  # node 0 is the depot

        for node in self.nodes[1:]:  # excludes the depot
            dnEdge = Edge(self.depot, node)  # creates the (depot, node) edge (arc)
            ndEdge = Edge(node, self.depot)
            dnEdge.invEdge = ndEdge  # sets the inverse edge (arc)
            ndEdge.invEdge = dnEdge
            # compute the Euclidean distance as cost
            # dnEdge.cost = math.sqrt((node.x - depot.x)**2 + (node.y - depot.y)**2)
            dnEdge.cost = self.distanceMatrix[node.ID][self.depot.ID]
            ndEdge.cost = dnEdge.cost  # assume symmetric costs
            # save in node a reference to the (depot, node) edge (arc)
            node.dnEdge = dnEdge
            node.ndEdge = ndEdge

    @staticmethod
    def readTestsToRun(testFile):

        with open(testFile) as file:
            lines = file.read().split('\n')
            lines.pop(0)  # remove the line with comments, i.e., the first line
        return lines

    """ From each line read before, return the instance name and parameters values """

    @staticmethod
    def getInstanceParameters(instanceName):

        line = instanceName.split()
        instance = line[0]
        beta1 = line[1]
        beta2 = line[2]
        vehCap = line[3]
        runTime = line[4]

        return instance, float(beta1), float(beta2), float(vehCap), float(runTime)
