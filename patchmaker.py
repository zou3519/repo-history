from abc import ABCMeta, abstractmethod
from patch import PatchSet


class PatchMaker(object):
    __metaclass__ = ABCMeta

    def __init__(self, pid_pool):
        self.pid_pool = pid_pool

    @abstractmethod
    def patches(self, old_corpus, new_corpus, rvid):
        """Get a patchset representing changes"""
        pass


class OldPatchMaker(PatchMaker):

    def patches(self, old_corpus, new_corpus, rvid):
        """Creates patches by diff-ing on a word-granularity"""

        old_corpus_words = old_corpus.split('\n')
        if old_corpus == '':
            old_corpus_words = []
        new_corpus_words = new_corpus.split('\n')
        result = PatchSet.psdiff(
            self.pid_pool, old_corpus_words, new_corpus_words, rvid)
        # print("patchset: ")
        # for patch in result.patches:
        #     print(patch.__dict__)
        # print("_____")
        return result
