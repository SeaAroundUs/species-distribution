import logging

import numpy as np

from species_distribution.models.world import Grid
from species_distribution.filters.filter import Filter


class LatitudeFilter(Filter):

    def filter(self, taxon, habitat):
        logging.debug('applying latitude filter')

        return self.probability_matrix


def filter(*args):
    f = LatitudeFilter()
    return f.filter(*args)
