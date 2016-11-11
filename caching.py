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


def save_to_cache(cachefile, model, content):
    """Save graph, model, and content to cache"""

    # Make cache folders if they don't exist
    if not os.path.isdir('GMLs'):
        os.mkdir('GMLs')
    if not os.path.isdir('models'):
        os.mkdir('models')
    if not os.path.isdir('content'):
        os.mkdir('content')

    # Writes graph to file
    nx.write_gml(model.graph, "GMLs/" + cachefile)

    # Write model to file
    modelFile = open("models/" + cachefile, "w")
    line = ""
    for patch in model.model:
        line += str(patch[0]) + ' ' + str(patch[1]) + '\n'
    modelFile.write(line)
    modelFile.close()

    # Write content to file
    contentFile = open("content/" + cachefile, "w")
    contentFile.write(content)
    contentFile.close()
    print ("Successfully wrote model to cache")


def read_cached_model(file):
    graphfile = 'GMLs/' + file
    contentfile = 'content/' + file
    modelfile = 'models/' + file

    graph = readGraph(graphfile)
    content = readContent(contentfile)
    model = readModel(modelfile)
    if graph is None or content is None or model is None:
        print ("Cached model missing components. Could not read.")
        return (None, None)
    print ("Successfully read cached model.")
    return (PatchModel(model, graph), content)


def readGraph(file):
    """Reads a networkx graph from a file for Wikipedia page"""
    print ("Reading graph . . .")
    if not os.path.isfile(file):
        return None
    return nx.read_gml(file)


def readContent(file):
    """Reads and returns a string from a file"""
    print ("Reading content . . .")
    if not os.path.isfile(file):
        return None

    contentFile = open(file, "r")
    content = ""
    for line in contentFile:
        content += line
    contentFile.close()
    return content


def readModel(file):
    """Reads and returns a PatchModel from a file"""
    print ("Reading model . . .")
    if not os.path.isfile(file):
        return None

    modelFile = open(file, "r")
    model = []

    # Read model
    for line in modelFile:
        line = line.split()
        model.append((int(line[0]), int(line[1])))
    modelFile.close()
    return model
