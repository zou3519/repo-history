from abc import ABCMeta, abstractmethod
import networkx as nx


class ScoreModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def score(self, nx_graph):
        """Return a mapping from patchid to score"""
        pass


class SimpleScoreModel(ScoreModel):

    def score(self, nx_graph):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("utf-8"))

            height = 0
            for (src, dst, prob) in nx_graph.out_edges_iter(node, data='prob'):
                if type(dst) != int:
                    dst = int(dst.decode("utf-8"))
                    src = int(src.decode("utf-8"))
                height += (height_dict[dst] + nx_graph.edge[src][dst]['dist']) * prob

            height_dict[node] = height

        return height_dict
