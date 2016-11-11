from abc import ABCMeta, abstractmethod
from patch import PatchSet


next_patch_id = 0  # next patch ID


class PatchMaker(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def patches(self, old_corpus, new_corpus, rvid):
        """Get a patchset representing changes"""
        pass


class OldPatchMaker(PatchMaker):

    def patches(self, old_corpus, new_corpus, rvid):
        """Creates patches by diff-ing on a word-granularity"""
        global next_patch_id

        old_corpus_words = old_corpus.split('\n')
        if old_corpus == '':
            old_corpus_words = []
        new_corpus_words = new_corpus.split('\n')
        result = PatchSet.psdiff(
            next_patch_id, old_corpus_words, new_corpus_words, rvid)
        # print("patchset: ")
        # for patch in result.patches:
        #     print(patch.__dict__)
        # print("_____")
        next_patch_id += len(result.patches)
        return result
