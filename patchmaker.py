from abc import ABCMeta, abstractmethod
from patch import PatchSet


class PatchMaker(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def patches(self, old_corpus, new_corpus, rvid):
        """Get a patchset representing changes"""
        pass


class OldPatchMaker(PatchMaker):
    patchid = 0

    def patches(self, old_corpus, new_corpus, rvid):
        """Creates patches by diff-ing on a word-granularity"""
        old_corpus_words = old_corpus.split('\n')
        if old_corpus == '':
            old_corpus_words = []
        new_corpus_words = new_corpus.split('\n')
        result = PatchSet.psdiff(
            self.patchid, old_corpus_words, new_corpus_words, rvid)
        print("patchset: ")
        for patch in result.patches:
            print(patch.__dict__)
        print("_____")
        self.patchid += len(result.patches)
        return result
