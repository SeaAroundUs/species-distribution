import numpy as np

from species_distribution.filters.filter import Filter


class DepthFilter(Filter):

    def _filter(self, taxon):

        probability_matrix = self.get_probability_matrix()
        return probability_matrix


_f = DepthFilter()


def filter(*args):
    return _f.filter(*args)
