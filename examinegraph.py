import json
import errno
import shutil
import os
from string import Template
from networkx.readwrite import json_graph

graph_template_path = 'webtemplates/graph/'
graph_template_file = 'template.html'
graph_generation_path = 'webgraphs/'


# def build_viz_from_file(name, gml_file):
#     nx_graph = readGraph(gml_file)
#     return build_viz_from_graph(name, nx_graph)


def build_viz_from_graph(name, nx_graph, score_dict):
    elements = graph_to_cytoscope(nx_graph, score_dict)

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


def graph_to_cytoscope(nx_graph, score_dict):
    nodes = []
    edges = []
    data = json_graph.node_link_data(nx_graph)

    for node in data['nodes']:
        node['score'] = score_dict[node['id']]
        nodes.append({'data': node})

    for link in data['links']:
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
