from abc import ABCMeta, abstractmethod


class CorpusDistModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def distance(self, old_corpus, new_corpus):
        """Computes the difference between two corpuses"""
        pass


class BasicDistanceModel(CorpusDistModel):
    """Distance between adjacent revisions is always 1"""

    def __init__(self, title):
        self.title = title

    def distance(self, previous, current):
        return 1
