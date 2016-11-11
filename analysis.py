#!/usr/bin/python
import argparse
from gitcorpus import *
from corpus import *
from distancemodel import *
from patchmaker import *
from scoremodel import *
from patch import *
from examinegraph import *
from heatmap import *
from caching import *
import util


def buildPatchGraph(file_context):
    """Builds a patch graph. Returns patch graph and distances to compute"""
    git_repo = GitRepo(file_context.repo_path)
    offset = 0  # Do not change, other offsets probably don't work.
    name = "bleh"
    corpus_rev_iter = GitRepoIter(
        name, git_repo, file_context.source_path, offset)
    patch_maker = OldPatchMaker()

    patch_model = PatchModel()
    prev_content = ''

    for (rvid, timestamp, content) in corpus_rev_iter:
        patch_set = patch_maker.patches(prev_content, content, rvid)
        for patch in patch_set.patches:
            patch_model.apply_patch(patch, timestamp)

        prev_content = content

    return patch_model


def parse_args():
    parser = argparse.ArgumentParser(usage='%%prog [options] source')

    parser.add_argument('source', nargs=1)
    parser.add_argument('--repo-path', dest='repo_path', type=str, required=True,
                        help='Path to the repo the file lives in.')
    parser.add_argument('--name', dest='name', type=str, required=True,
                        help='The name of this analysis')

    return parser.parse_args()


def create_patch_models(analysis_name, analysis_context, check_cache=True, save_to_cache=True):
    """First phase of the analysis: generate patch models"""

    repo_path = analysis_context.repo_path
    source_path = analysis_context.source_path

    if check_cache:
        patch_graphs_dict = read_patch_models(analysis_name)
        if patch_graphs_dict is not None:
            print "Read cached patch models"
            return patch_graphs_dict

    files = util.files(repo_path, source_path)
    file_contexts = map(lambda file: GitContext(repo_path, file), files)
    patch_graphs = map(lambda context: buildPatchGraph(context), file_contexts)
    patch_graphs_dict = dict(zip(files, patch_graphs))

    if save_to_cache:
        save_patch_models(analysis_name, patch_graphs_dict)

    return patch_graphs_dict


def required_distances(nx_graph):

    required_distances = set()
    node_list = nx.topological_sort(nx_graph, reverse=True)
    for node in node_list:
        if type(node) != int:
            node = int(node.decode("ascii"))

        for (src, dst) in nx_graph.out_edges_iter(node):

            if type(dst) != int:
                dst = int(dst.decode("ascii"))
            if type(src) != int:
                src = int(src.decode("ascii"))

            src_rev = eval(nx_graph.node[src]['patch'])['revision']
            dst_rev = eval(nx_graph.node[dst]['patch'])['revision']
            required_distances.add((dst_rev, src_rev))

    return required_distances


def compute_distances(analysis_name, analysis_context, patch_graphs_dict, distance_model_ctor, check_cache=True, save_to_cache=True):
    """Phase II: Generate distances"""

    distance_model = distance_model_ctor()
    descriptor = distance_model.__class__.__name__

    if check_cache:
        distances_obj = Distances.read_from_file(analysis_name, descriptor)
        if distances_obj is not None:
            print "Read cached distances object %s" % descriptor
            return distances_obj

    required_dists_sets = map(lambda patch_model: required_distances(
        patch_model.graph), patch_graphs_dict.values())
    required = util.flattensets(required_dists_sets)
    dists_dict = {}
    for (dst_rev, src_rev) in required:
        dist = distance_model.distance(analysis_context, dst_rev, src_rev)
        dists_dict[(dst_rev, src_rev)] = dist

    distances = Distances(analysis_name, dists_dict, descriptor)
    if save_to_cache:
        distances.save_to_file()
    return distances


def compute_scores_helper(analysis_context, patch_model, distances_dict, score_model_ctor):
    score_model = score_model_ctor()
    score_dict = score_model.score(
        patch_model.graph, distances_dict, analysis_context)
    return score_dict


def compute_scores(analysis_name, analysis_context, patch_graphs_dict, distances, score_model_ctor, check_cache=True, save_to_cache=True):
    """Phase III: Generate scores"""

    descriptor = score_model_ctor().__class__.__name__

    if check_cache:
        full_descriptor = descriptor + "_" + distances.descriptor
        scores_obj = Scores.read_from_file(analysis_name, full_descriptor)
        if scores_obj is not None:
            print "Read cached scores object %s" % full_descriptor
            return scores_obj

    scores_dicts = map(lambda patch_model: compute_scores_helper(
        analysis_context, patch_model, distances.dict, score_model_ctor), patch_graphs_dict.values())
    scores_dict = {}
    for partial_dict in scores_dicts:
        scores_dict.update(partial_dict)

    scores = Scores(analysis_name, scores_dict,
                    descriptor, distances.descriptor)
    if save_to_cache:
        scores.save_to_file()
    return scores


def main():
    args = parse_args()
    analysis_name = args.name
    repo_path = args.repo_path
    source_path = args.source[0]
    analysis_context = GitContext(repo_path, source_path)

    patch_graphs_dict = create_patch_models(analysis_name, analysis_context)
    distances = compute_distances(
        analysis_name, analysis_context, patch_graphs_dict, BasicDistanceModel)
    scores = compute_scores(
        analysis_name, analysis_context, patch_graphs_dict, distances, SimpleScoreModel)

    print distances.dict
    print scores.dict

    # # # build patch graph
    # print(files)
    # (patch_model, content, score_dict) = applyCodeModel(
    #     args.name, args.source[0], args.repo_path)
    # print ("Building patch model viz . . .")
    # build_viz_from_graph(args.name, patch_model.graph, score_dict)
    # print ("Building heatmap . . .")
    # build_heatmap(args.name, patch_model.model, content, score_dict)


if __name__ == "__main__":
    main()
