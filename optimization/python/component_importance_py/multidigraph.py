
import networkx as networkx


def is_eulerian(G):
    """Return True if G is an Eulerian graph and therefore has an Eulerian cycle.
    # Examples:
    # >>> is_eulerian(networkx.DiGraph({0:[3], 1:[2], 2:[3], 3:[0, 1]}))
    # True
    # >>> is_eulerian(networkx.complete_graph(5))
    # True
    # >>> is_eulerian(networkx.petersen_graph())
    False
    """

    if networkx.is_directed(G):
        # Every node of a directed Eulerian graph needs to have
        # equal indegree and outdegree.
        if not networkx.is_strongly_connected(G):
            return False
        nodeWithoutSameInOutDegree = 0
        nodes = []
        for n in G.nodes_iter():
            if G.in_degree(n) != G.out_degree(n):
                return False
    # if two of the nodes have odd degree, there
    # could still be an Eulerian path. (not implemented!)
    # ~ nodes.append(n)
    # ~ nodeWithoutSameInOutDegree += 1
    # ~ if nodeWithoutSameInOutDegree == 0:
    # ~ return True
    # ~ if nodeWithoutSameInOutDegree == 2:
    # ~ NodeOneInDeg  = G.in_degree(nodes[0])
    # ~ NodeOneOutDeg = G.out_degree(nodes[0])
    # ~ NodeTwoInDeg  = G.in_degree(nodes[1])
    # ~ NodeOneOutDeg = G.out_degree(nodes[1])
    # ~ if ((NodeOneInDeg - NodeOneOutDeg == 1 or NodeOneOutDeg - NodeOneInDeg == 1) and\
    # ~ (NodeTwoInDeg - NodeOneOutDeg == 1 or NodeOneOutDeg - NodeTwoInDeg == 1)):
    # ~ return True
    # ~ return False
    else:
        # An undirected Eulerian graph has no vertices of odd degrees.
        if not networkx.is_connected(G):
            return False
        for deg in G.degree_iter():
            if deg[1] % 2 != 0:
                return False
    return True


def eulerian_circuit(G, edges=True, source=None):
    """Return the visited nodes or edges of the Eulerian circuit.
        edges: if true, visited edges are returned, otherwise visited nodes
        source: starting node
    Examples:
    # >>> eulerian_circuit(networkx.complete_graph(5))
    # [(0, 1), (1, 2), (2, 0), (0, 3), (3, 1), (1, 4), (4, 2), (2, 3), (3, 4), (4, 0)]
    # >>> eulerian_circuit(networkx.complete_graph(5), False, 4)
    # [4, 0, 1, 2, 0, 3, 1, 4, 2, 3, 4]
    # >>> eulerian_circuit(networkx.MultiDiGraph({0:[1], 1:[2, 2], 2:[1]}))
    # False
    """

    if not is_eulerian(G):
        return False
    edge_list = []
    node_list = []
    g = G.copy()

    # Get the first vertex
    if source is None:
        n = g.nodes_iter().next()
    else:
        n = source
    node_list.append(n)
    while g.size() > 0:
        for e in g.edges([n]):
            g.remove_edge(e[0], e[1])
            if networkx.is_connected(g):
                break
            else:
                g.add_edge(e[0], e[1])
        else:
            # We have to cross a bridge.
            # If cutting an edge would cause the graph to be disconnected,
            # that edge is called a bridge.
            g.remove_edge(e[0], e[1])
            g.remove_node(n)
        if n == e[0]:
            n = e[1]
        else:
            n = e[0]
            e = (e[1], e[0])  # reverse the list
        edge_list.append(e)
        node_list.append(n)

    if edges:
        return edge_list
    else:
        return node_list


if __name__ == "__main__":
    # ~ g2 = networkx.DiGraph({0:[3], 1:[2], 2:[3], 3:[0, 1]})
    # ~ g3 = networkx.MultiDiGraph({0:[1], 1:[2, 2], 2:[1]})
    # ~ g = networkx.complete_graph(5)
    # ~ print is_eulerian(g2)
    eulerian_circuit(networkx.MultiDiGraph({0: [1], 1: [2, 2], 2: [1]}))