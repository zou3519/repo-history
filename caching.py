import os
import networkx as nx
from patch import PatchModel
import cPickle as pickle
import errno


def create_required_folders(path):
    index = path.rfind('/')
    if index == -1:
        return

    try:
        os.makedirs(path[:index])
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def analysis_folder(analysis_name):
    return 'analysis/%s/' % analysis_name


def analysis_graph_folder(analysis_name):
    return analysis_folder(analysis_name) + 'graphs/'


def graph_dict_filename(analysis_name):
    return analysis_graph_folder(analysis_name) + 'graph_dict.p'


def distances_obj_filename(analysis_name, dist_type):
    return '%sdists/%s.p' % (analysis_folder(analysis_name), dist_type)


def scores_obj_filename(analysis_name, score_type):
    return '%sscores/%s.p' % (analysis_folder(analysis_name), score_type)


def save_patch_models(analysis_name, patch_graphs_dict):
    """patch_graph_dict: source file => patch model"""
    graph_dict = {}
    counter = 0
    create_required_folders(analysis_graph_folder(analysis_name))
    for (file, patch_model) in patch_graphs_dict.iteritems():
        filename = '%d.pmodel.p' % counter
        counter += 1
        graph_dict[file] = filename
        patch_model.save_to_file(
            analysis_graph_folder(analysis_name) + filename)
    graph_dict_fn = graph_dict_filename(analysis_name)
    pickle.dump(graph_dict, open(graph_dict_fn, 'wb'))


def read_patch_models(analysis_name):
    graph_dict_file = graph_dict_filename(analysis_name)
    if not os.path.isfile(graph_dict_file):
        return None

    # Assumption: if the graph dict file exists, the patch models do too
    graph_dict = pickle.load(open(graph_dict_file, 'rb'))
    result = {}
    for source_file, saved_file in graph_dict.iteritems():
        result[source_file] = PatchModel.read_from_file(
            analysis_graph_folder(analysis_name) + saved_file)
    return result


def read_patch_models_partial(analysis_name, filekeys):
    graph_dict_file = graph_dict_filename(analysis_name)
    if not os.path.isfile(graph_dict_file):
        return None

    graph_dict = pickle.load(open(graph_dict_file, 'rb'))
    for filekey in filekeys:
        assert(filekey in graph_dict)

    result = {}
    for filekey in filekeys:
        saved_file = graph_dict[filekey]
        result[filekey] = PatchModel.read_from_file(
            analysis_graph_folder(analysis_name) + saved_file)

    return result
