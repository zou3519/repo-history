from abc import ABCMeta, abstractmethod
import networkx as nx


class ScoreModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def score(self, nx_graph):
        """Return a mapping from patchid to score"""
        pass


class SimpleScoreModel(ScoreModel):

    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            for (src, dst, prob) in nx_graph.out_edges_iter(node, data='prob'):
                if type(dst) != int:
                    dst = int(dst.decode("ascii"))
                    src = int(src.decode("ascii"))
                src_rev = nx_graph.node[src]['rev']
                dst_rev = nx_graph.node[dst]['rev']
                key = (dst_rev, src_rev, filekey)
                if key not in distance_dict:
                    print "could not find key computation"
                edge_value = distance_dict[key]
                height += (height_dict[dst] + edge_value) * prob

            height_dict[node] = height

        return height_dict


class TimeWeightedScoreModel(ScoreModel):

    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            for (src, dst, prob) in nx_graph.out_edges_iter(node, data='prob'):
                if type(dst) != int:
                    dst = int(dst.decode("ascii"))
                    src = int(src.decode("ascii"))

                src_rev = nx_graph.node[src]['rev']
                dst_rev = nx_graph.node[dst]['rev']

                src_time = nx_graph.node[src]['time']
                dst_time = nx_graph.node[dst]['time']
                weeks = (src_time - dst_time) / (86400*7) # seconds in a week
                weight = 1 # TODO: a lil sketch
                if weeks != 0:
                    weight = 1/weeks

                key = (dst_rev, src_rev, filekey)
                if key not in distance_dict:
                    print "could not find key computation"
                edge_value = distance_dict[key]
                height += (height_dict[dst] + edge_value*weight) * prob

            height_dict[node] = height

        return height_dict
