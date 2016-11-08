#!/usr/bin/python3
import argparse
from gitcorpus import *
from corpus import *
from distancemodel import *
from patchmaker import *
from scoremodel import *
from patch import *
from examinegraph import *
from heatmap import *


def applyCodeModel(name, source, repo_path):
    git_repo = GitRepo(repo_path)
    offset = 0  # Do not change, other offsets probably don't work.

    code_iterable = GitRepoIter(name, git_repo, source, offset)
    distance_model = BasicDistanceModel(name)
    patch_maker = OldPatchMaker()
    score_model = SimpleScoreModel()

    (patch_model, content) = buildPatchModel(code_iterable, distance_model, patch_maker)
    score_dict = score_model.score(patch_model.graph)

    return (patch_model, content, score_dict)


def buildPatchModel(corpus_rev_iter, dist_model, patch_maker):

    patch_model = PatchModel()
    prev_content = ''

    for (rvid, timestamp, content) in corpus_rev_iter:
        dist = dist_model.distance(prev_content, content)
        patch_set = patch_maker.patches(prev_content, content, rvid)
        for patch in patch_set.patches:
            patch_model.apply_patch(patch, timestamp, dist)

        prev_content = content

    return (patch_model, prev_content)


def parse_args():
    parser = argparse.ArgumentParser(usage='%%prog [options] source')

    parser.add_argument('source', nargs=1)
    parser.add_argument('--repo-path', dest='repo_path', type=str, required=True,
                        help='Path to the repo the file lives in.')
    parser.add_argument('--name', dest='name', type=str, required=True,
                        help='The name of this analysis/output files')

    return parser.parse_args()


def main():
    args = parse_args()
    (patch_model, content, score_dict) = applyCodeModel(
        args.name, args.source[0], args.repo_path)
    build_viz_from_graph(args.name, patch_model.graph, score_dict)
    build_heatmap(args.name, patch_model.model, content, score_dict)


if __name__ == "__main__":
    # execute only if run as a script
    main()
