import logging

import numpy as np

from species_distribution.models.db import session
from species_distribution.models.taxa import TaxonHabitat
from species_distribution.filters.filter import Filter


class MembershipFunction():
    """ give break points for 3 membership categories:
    e.g. [[25, 50, 100, 150]]"""

    def __init__(self, break_points):
        self.break_points = (0, ) + tuple(break_points)

    def values(self, value):
        return self.small(value), self.medium(value), self.large(value)

    def small(self, value):
        y_coords = (1, 1, 0, 0, 0)
        return np.interp(value, self.break_points, y_coords)

    def medium(self, value):
        y_coords = (0, 0, 1, 1, 0)
        return np.interp(value, self.break_points, y_coords)

    def large(self, value):
        y_coords = (0, 0, 0, 0, 1)
        return np.interp(value, self.break_points, y_coords)


class HabitatFilter(Filter):

    def versatility(self, taxon):
        """ membership function for versatility.  14-4.pdf pp. 32 """
        versatility_function = MembershipFunction((.25, .5, .5, .75))

    def maximum_length(self, taxon):
        """ membership function for maximum length.  14-4.pdf pp. 32 """
        maximum_length_function = MembershipFunction((25, 50, 100, 150))

    def filter(self, taxon, habitat):
        raise NotImplementedError

        logging.debug('applying habitat filter')

        sesh = session()

        habitat = sesh.query(TaxonHabitat).get(taxon.taxonkey)

        return self.probability_matrix


def filter(*args):
    f = HabitatFilter()
    return f.filter(*args)
