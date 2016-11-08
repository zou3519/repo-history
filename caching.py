import os
import networkx as nx
from patch import PatchModel


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
