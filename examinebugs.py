#!/usr/bin/python
import argparse
from gitcorpus import *
from caching import read_patch_models
from distancemodel import Scores
import pandas as pd
from analysis import *


# def main():
#     args = parse_args()
#     repo_path = args.repo_path
#     source_path = args.source[0]
#     analysis_name = args.name
#     dist_desc = args.distmodel # 'BasicDistanceModel'
#     score_desc = args.scoremodel # 'SimpleScoreModel'

#     df = examinebugs(repo_path, source_path, analysis_name, dist_desc, score_desc)
#     df.to_csv("test.csv")


def main():
    distmodels = ["BasicDistanceModel", "GitDiffDistModel", "MossDistModel", "PatientDiffDistModel"]
    scoremodels = ["SimpleScoreModel", "LongestScoreModel", "ShortestScoreModel", "InEdgesScoreModel",
        "OutEdgesScoreModel", "SizeScoreModel", "TimeWeightedScoreModel"]

    for distmodel in distmodels:
        for scoremodel in scoremodels:
            print "Start analysis %s %s" % (distmodel, scoremodel)
            run_analysis(16, "mm", "/home/cat/rzou/linux/", "mm", distmodel, scoremodel)

    df = None
    for distmodel in distmodels:
        for scoremodel in scoremodels:
            print "Data collection for %s %s" % (distmodel, scoremodel)
            nextdf = examinebugs("/home/cat/rzou/linux/", "mm", "mm", distmodel, scoremodel)
            if df is None:
                df = nextdf
            else:
                col = scoremodel + "_" + distmodel
                df[col] = nextdf[col]
    df.to_csv("test.csv")



def examinebugs(repo_path, source_path, analysis_name, dist_desc, score_desc):
    analysis_context = GitContext(repo_path, source_path)

    patch_graphs_dict = read_patch_models(analysis_name)
    if patch_graphs_dict is None:
        print("Could not find cached patch graph")
        return
    print "Read patch models"

    (revs, msgs) = zip(*bugfix_revisions(analysis_context, 'bugzilla'))
    bug_rating_dict = compute_bug_ratings(patch_graphs_dict, revs)
    print "Computed bug ratings"
    # print(bug_rating_dict)

    scores_obj = Scores.read_from_file(analysis_name, score_desc + "_" + dist_desc)
    if scores_obj is None:
        print("Could not find cached scores")
        return

    # Write csv of (pid, score, rating)
    print "Creating output csv"

    patches = []
    scores = []
    ratings = []

    series_name = score_desc + "_" + dist_desc
    for pid, score in scores_obj.dict.iteritems():
        rating = 0
        if pid in bug_rating_dict:
            rating = bug_rating_dict[pid]
            assert(rating != 0)
        patches.append(pid)
        scores.append(score)
        ratings.append(rating)

    dic = {series_name: scores, 'rating': ratings }
    df = pd.DataFrame(dic, index=patches)
    return df


def parse_args():
    parser = argparse.ArgumentParser(usage='%%prog [options] source')

    parser.add_argument('source', nargs=1)
    parser.add_argument('--repo-path', dest='repo_path', type=str, required=True,
                        help='Path to the repo the file lives in.')
    parser.add_argument('--name', dest='name', type=str, required=True,
                        help='The name of this analysis')
    # e.g. BasicDistanceModel
    parser.add_argument('--distmodel', dest='distmodel', type=str, required=True,
                        help='Distance model used')
    # e.g. SimpleScoreModel
    parser.add_argument('--scoremodel', dest='scoremodel', type=str, required=True,
                        help='Score model used')


    return parser.parse_args()


def bugfix_revisions(analysis_context, fix_identifier):
    """Get bugfix revisions. Returns list of (rev, short message)"""
    rev_hash_len = 40
    repo = GitRepo(analysis_context.repo_path)
    (exit_code, raw_out, err) = repo.log_line_with_grep(
        fix_identifier, analysis_context.source_path)
    if exit_code:
        print("problem: %s" % err)
        raise err

    result = []
    for line in raw_out.split('\n'):
        result.append((line[0:rev_hash_len], line[(rev_hash_len + 1):]))
    return result


def compute_bug_ratings(patch_models_dict, bugfix_revs):
    """Return a pid -> bug rating dict"""

    patch_models = patch_models_dict.values()
    rating_dicts_lst = map(lambda r: rev_to_bug_rating(
        patch_models, r), bugfix_revs)

    result = {}
    for rating_dicts in rating_dicts_lst:
        for rating_dict in rating_dicts:
            for pid, rating in rating_dict.iteritems():
                if pid not in result:
                    result[pid] = 0
                result[pid] += rating

    return result


def rev_to_bug_rating(patch_models, bugfix_rev):
    return map(lambda m: bug_rating_dict(m, bugfix_rev), patch_models)


def bug_rating_dict(patch_model, bugfix_rev):
    """Returns patch id -> bug rating dict"""
    nx_graph = patch_model.graph
    if bugfix_rev not in patch_model.rev_to_pids:
        return {}

    rev_pids = patch_model.rev_to_pids[bugfix_rev]
    result = {}
    for rev_pid in rev_pids:
        for (src, dst, prob) in nx_graph.out_edges_iter(rev_pid, data='prob'):
            dst_pid = (eval(nx_graph.node[dst]['patch'])['pid'])
            # dst_pid = nx_graph.node[dst]['id']
            if dst_pid not in result:
                result[dst_pid] = 0
            result[dst_pid] += prob

    return result


if __name__ == "__main__":
    main()
