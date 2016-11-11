from abc import ABCMeta, abstractmethod
import cPickle as pickle
from caching import *


class CorpusDistModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def distance(self, old_corpus, new_corpus):
        """Computes the difference between two corpuses"""
        pass


class BasicDistanceModel(CorpusDistModel):
    """Distance between adjacent revisions is always 1"""

    def distance(self, analysis_context, old_rev, new_rev):
        return 1 if old_rev != new_rev else 0


class Distances(object):

    def __init__(self, analysis_name, dists_dict={}, descriptor="None"):
        self.analysis_name = analysis_name
        self.dict = dists_dict
        self.descriptor = descriptor

    def save_to_file(self):
        filename = distances_obj_filename(self.analysis_name, self.descriptor)
        create_required_folders(filename)
        pickle.dump(self, open(filename, 'wb'))

    @classmethod
    def read_from_file(cls, analysis_name, descriptor):
        filename = distances_obj_filename(analysis_name, descriptor)
        if not os.path.isfile(filename):
            return None
        return pickle.load(open(filename, 'rb'))


class Scores(object):

    def __init__(self, analysis_name, scores_dict={}, descriptor="None", dists_descriptor="None"):
        self.dict = scores_dict
        self.analysis_name = analysis_name
        self.descriptor = descriptor
        self.dists_descriptor = dists_descriptor

    @property
    def full_descriptor(self):
        return "%s_%s" % (self.descriptor, self.dists_descriptor)

    def save_to_file(self):
        """Save without the distances_obj"""
        filename = scores_obj_filename(self.analysis_name, self.full_descriptor)
        create_required_folders(filename)
        pickle.dump(self, open(filename, 'wb'))

    @classmethod
    def read_from_file(cls, analysis_name, full_descriptor):
        filename = scores_obj_filename(analysis_name, full_descriptor)
        if not os.path.isfile(filename):
            return None
        return pickle.load(open(filename, 'rb'))
