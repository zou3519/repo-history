from abc import ABCMeta, abstractmethod


class CorpusRevisionIter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        """Get an iterator"""
        pass
