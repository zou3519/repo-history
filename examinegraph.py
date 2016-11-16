#!/usr/bin/python
import argparse
import json
import errno
import shutil
import os
from string import Template
from networkx.readwrite import json_graph
from caching import *
from distancemodel import *

graph_template_path = 'webtemplates/graph/'
graph_template_file = 'template.html'
graph_generation_path = 'webgraphs/'


def main():
    args = parse_args()
    examine_graph(args.analysis_name, args.filekey,
                  args.dist_descriptor, args.score_descriptor, args.outfile_name)
    os.system('google-chrome %s%s/%s' %
              (graph_generation_path, args.outfile_name, graph_template_file))


def parse_args():
    parser = argparse.ArgumentParser(usage='%%prog [options]')
    parser.add_argument('--analysis-name', dest='analysis_name', type=str, required=True,
                        help='Name of the analysis to examine')
    parser.add_argument('--filekey', dest='filekey', type=str, required=True,
                        help='The filename of the original file')
    parser.add_argument('--dist-desc', dest='dist_descriptor', type=str, required=True,
                        help='The name of the distance metric used')
    parser.add_argument('--score-desc', dest='score_descriptor', type=str, required=True,
                        help='The name of the score metric used')
    parser.add_argument('--out', dest='outfile_name', type=str, required=True,
                        help='Where to save the visualization')
    return parser.parse_args()


def examine_graph(analysis_name, filekey, dist_descriptor, score_descriptor, outfile_name):
    """
    Visualize the patch graph built by the analysis.
    Analysis files must already exist
    """
    patch_models = read_patch_models_partial(analysis_name, [filekey])
    if patch_models is None:
        print("Could not read saved patch model. Does it exist?")
        return

    assert(len(patch_models.keys()) == 1)
    patch_model = patch_models[filekey]

    distances = Distances.read_from_file(analysis_name, dist_descriptor)
    full_descriptor = score_descriptor + "_" + dist_descriptor
    scores = Scores.read_from_file(analysis_name, full_descriptor)

    build_viz_from_graph(outfile_name, patch_model.graph, distances, scores)


def build_viz_from_graph(name, nx_graph, distances, scores):
    elements = graph_to_cytoscope(nx_graph, distances, scores)

    nx.write_graphml(nx_graph, "/home/rzou/Dropbox/kleebox/" + name + ".xml")
    # inject elements into new html file
    graph_path = graph_generation_path + name
    template_file = graph_path + '/' + graph_template_file
    copy(graph_template_path, graph_generation_path + name)
    new_content = ''

    with open(template_file, 'r') as content_file:
        template = Template(content_file.read())
        new_content = template.safe_substitute(elements=elements)
    with open(template_file, 'w') as content_file:
        content_file.write(new_content)


def graph_to_cytoscope(nx_graph, distances, scores):
    nodes = []
    edges = []
    data = json_graph.node_link_data(nx_graph)

    for node in data['nodes']:
        node['score'] = scores.dict[node['id']]
        nodes.append({'data': node})

    for link in data['links']:
        src_rev = nodes[link['source']]['data']['rev']
        tgt_rev = nodes[link['target']]['data']['rev']
        dist = distances.dict[(tgt_rev, src_rev)]
        link['dist'] = dist
        link['source'] = nodes[link['source']]['data']['id']
        link['target'] = nodes[link['target']]['data']['id']
        edges.append({'data': link})

    return json.dumps({'nodes': nodes, 'edges': edges})


def copy(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)

    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
            return
        print('Directory not copied. Error: %s' % e)


if __name__ == "__main__":
    main()
