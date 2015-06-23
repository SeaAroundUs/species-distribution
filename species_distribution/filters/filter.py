import functools
import itertools
import logging

import numpy as np

from species_distribution.models.world import Grid


class BaseFilter():
    """ subclasses of Filter should define a _filter method
    which will be called by filter
    """

    def __init__(self):
        self.grid = Grid()
        self.logger = logging.getLogger(__name__)

    def get_probability_matrix(self):
        return np.ma.MaskedArray(data=np.full(self.grid.shape, np.nan, dtype=float), mask=True)

    @classmethod
    def filter(cls, *args, **kwargs):
        instance = cls()
        instance.logger.debug('applying {}'.format(cls.__module__))
        probability = instance._filter(*args, **kwargs)

        max = probability.max()
        assert(
            max is np.ma.masked
            or
            (max <= 1 and probability.min() >= 0)
        )

        return probability

    @functools.lru_cache(maxsize=2**20)
    def depth_probability(self, seafloor_depth, taxon_mindepth, taxon_maxdepth):
        """
        calculates probability of taxon in seafloor_depth of water based on a
        triangular distribution with maximum at 1/3 down

        currently used by depth and submergence filters

        parameters
        seafloor_depth of seafloor (in negative meters)
        taxon_mindepth of taxon (closer to surface, in negative meters)
        taxon_maxdepth of taxon (further from surface, in negative meters)

        """

        # create scalene triangle properties
        one_third_depth = taxon_mindepth - (taxon_mindepth - taxon_maxdepth) / 3

        # area of triangle is 1/2 * base * height.
        # height = 1 (maximum probability), so just base / 2
        triangle_area = (taxon_mindepth - taxon_maxdepth) / 2
        xp = [taxon_maxdepth, one_third_depth, taxon_mindepth]
        fp = [0, 1, 0]

        interpolated_value = np.interp([seafloor_depth], xp, fp)[0]

        # create list of (Z,P) tuples where Z = depth and P = probabilty
        # order by depth, and cast out everything outside the world range
        # what is left can be integrated and divided by total area to get
        # cell probability

        ZP = sorted(itertools.chain(zip(xp, fp), ((seafloor_depth, interpolated_value),)))
        ZP_in_range = list(filter(lambda x: x[0] >= seafloor_depth, ZP))
        x, y = zip(*ZP_in_range)

        probability = np.trapz(y, x) / triangle_area

        # floating point error is pushing result ever so slightly above 1, clip it
        return np.clip(probability, 0, 1)
