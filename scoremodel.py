from abc import ABCMeta, abstractmethod
import networkx as nx


class ScoreModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def score(self, nx_graph):
        """Return a mapping from patchid to score"""
        pass


class SimpleScoreModel(ScoreModel):

    def score(self, nx_graph, distance_dict, analysis_context):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        print(node_list)

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            for (src, dst, prob) in nx_graph.out_edges_iter(node, data='prob'):
                if type(dst) != int:
                    dst = int(dst.decode("ascii"))
                    src = int(src.decode("ascii"))
                src_rev = eval(nx_graph.node[src]['patch'])['revision']
                dst_rev = eval(nx_graph.node[dst]['patch'])['revision']
                key = (dst_rev, src_rev)
                if key not in distance_dict:
                    print "could not find key computation"
                edge_value = distance_dict[key]
                height += (height_dict[dst] + edge_value) * prob

            height_dict[node] = height

        return height_dict
