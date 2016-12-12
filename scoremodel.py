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


class LongestScoreModel(ScoreModel):


    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            max_len = -1
            use_dst = None
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
                if edge_value > max_len:
                    max_len = edge_value
                    use_dst = dst

            if use_dst is None:
                height_dict[node] = 0
            else:
                height_dict[node] = height_dict[use_dst] + max_len

        return height_dict


class ShortestScoreModel(ScoreModel):


    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            min_len = 1e999
            use_dst = None
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
                if edge_value < min_len:
                    min_len = edge_value
                    use_dst = dst

            if use_dst is None:
                height_dict[node] = 0
            else:
                height_dict[node] = height_dict[use_dst] + min_len

        return height_dict


class InEdgesScoreModel(ScoreModel):


    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = 0
            for (src, dst, prob) in nx_graph.in_edges_iter(node, data='prob'):
                if type(dst) != int:
                    dst = int(dst.decode("ascii"))
                    src = int(src.decode("ascii"))
                src_rev = nx_graph.node[src]['rev']
                dst_rev = nx_graph.node[dst]['rev']
                key = (dst_rev, src_rev, filekey)
                if key not in distance_dict:
                    print "could not find key computation"
                edge_value = distance_dict[key]
                height = edge_value

            height_dict[node] = height

        return height_dict


class OutEdgesScoreModel(ScoreModel):


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
                height = edge_value

            height_dict[node] = height

        return height_dict


class SizeScoreModel(ScoreModel):


    def score(self, nx_graph, distance_dict, analysis_context, filekey):
        """Compute weighted distance to the root node"""
        node_list = nx.topological_sort(nx_graph, reverse=True)
        height_dict = {}

        for node in node_list:
            if type(node) != int:
                node = int(node.decode("ascii"))

            height = nx.get_node_attributes(nx_graph, 'size')[node]

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
