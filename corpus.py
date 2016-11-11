from abc import ABCMeta, abstractmethod


class CorpusContext(object):
    """Information about the corpus being analyzed"""
    __metaclass__ = ABCMeta


class CorpusRevisionIter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        """Get an iterator"""
        pass
