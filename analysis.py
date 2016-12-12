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
from pathos.multiprocessing import ProcessingPool
import util
from mossdist import MossDistModel


# Number of processes to use. Yes, processes, not threads.
nthreads = 1


def buildPatchGraph(file_context, pid_pool):
    """Builds a patch graph. Returns patch graph and distances to compute"""
    git_repo = GitRepo(file_context.repo_path)
    offset = 0  # Do not change, other offsets probably don't work.
    name = "bleh"  # TODO: get rid of this
    print(file_context.source_path)
    corpus_rev_iter = GitRepoIter(
        name, git_repo, file_context.source_path, offset)
    patch_maker = OldPatchMaker(pid_pool)

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
    parser.add_argument('--distmodel', dest='distmodel', type=str, required=True,
                        help='Distance model name (GitDiffDistModel | MossDistModel)')
    parser.add_argument('--nthreads', dest='nthreads', type=int, default=1,
                        help='Number of processes to run')
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
    num_files = len(files)
    file_contexts = map(lambda file: GitContext(repo_path, file), files)
    pid_pools = map(lambda k: PidPool(k, num_files), xrange(len(files)))

    mapfn = pp_mapfn()
    patch_graphs = mapfn(lambda args: buildPatchGraph(
        *args), zip(file_contexts, pid_pools))

    patch_graphs_dict = dict(zip(files, patch_graphs))

    if save_to_cache:
        save_patch_models(analysis_name, patch_graphs_dict)

    return patch_graphs_dict


def pp_mapfn():
    if nthreads <= 1:
        return map

    pool = ProcessingPool(nthreads)
    return pool.map


def required_distances(key, nx_graph):

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

            src_rev = nx_graph.node[src]['rev']
            dst_rev = nx_graph.node[dst]['rev']
            required_distances.add((dst_rev, src_rev, key))

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

    # (rev, rev, None | filekey) 
    required_dists_sets = map(lambda (key, patch_model): required_distances(key,
        patch_model.graph), patch_graphs_dict.iteritems())
    required = util.flattensets(required_dists_sets)
    dists_dict = {}

    mapfn = pp_mapfn()
    dists = mapfn(lambda (dst_rev, src_rev, filekey): distance_model.distance(
        analysis_context, dst_rev, src_rev, filekey), required)
    dists_dict = dict(zip(required, dists))

    distances = Distances(analysis_name, dists_dict, descriptor)
    if save_to_cache:
        distances.save_to_file()
    return distances


def compute_scores_helper(analysis_context, patch_model, filekey, distances_dict, score_model_ctor):
    score_model = score_model_ctor()
    score_dict = score_model.score(
        patch_model.graph, distances_dict, analysis_context, filekey)
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

    scores_dicts = map(lambda (filekey, patch_model): compute_scores_helper(
        analysis_context, patch_model, filekey, distances.dict, score_model_ctor), patch_graphs_dict.iteritems())
    scores_dict = {}
    for partial_dict in scores_dicts:
        scores_dict.update(partial_dict)

    scores = Scores(analysis_name, scores_dict,
                    descriptor, distances.descriptor)
    if save_to_cache:
        scores.save_to_file()
    return scores


def git_diff_dist_model_ctor(repo_path):
    return (lambda: GitDiffDistModel(repo_path))


def get_dist_model_ctor(name, repo_path):
    if name == 'MossDistModel':
        return MossDistModel
    elif name == 'GitDiffDistModel':
        return git_diff_dist_model_ctor(repo_path)
    elif name == 'BasicDistanceModel':
        return BasicDistanceModel 
    else:
        assert(False)


def main():
    global nthreads

    args = parse_args()
    nthreads = args.nthreads
    analysis_name = args.name
    repo_path = args.repo_path
    source_path = args.source[0]
    dist_model_name = args.distmodel
    analysis_context = GitContext(repo_path, source_path)

    print("Entering patch model phase")
    patch_graphs_dict = create_patch_models(analysis_name, analysis_context)
    print("Entering distances phase")
    dist_model_ctor = get_dist_model_ctor(dist_model_name, repo_path)
    distances = compute_distances(
        analysis_name, analysis_context, patch_graphs_dict, dist_model_ctor)
    print("Entering scores phase")
    scores = compute_scores(
        analysis_name, analysis_context, patch_graphs_dict, distances, SimpleScoreModel)

    # print distances.dict
    # print scores.dict

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
