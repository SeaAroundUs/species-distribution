import functools
import itertools
import logging

import numpy as np

from species_distribution.models.db import Session
from species_distribution.models.taxa import Taxon
from species_distribution.models.world import Grid
from species_distribution.settings import NUMPY_WARNINGS


class MetaBaseFilter(type):
    @property
    def name(cls):
        return cls.__module__.split('.')[-1]

class BaseFilter(metaclass=MetaBaseFilter):
    """ subclasses of Filter should define a _filter method
    which will be called by filter.  It should accept two keyword
    arguments:

    _filter(taxon=None, session=None)

    taxon should be a taxon ID which will be converted to a Taxon object
    and the SQLAlchemy session will be passed in by filter

    """

    def __init__(self):
        self.grid = Grid()
        self.logger = logging.getLogger(__name__)
        np.seterrcall(self.logger.warn)
        np.seterr(all=NUMPY_WARNINGS)
        self.probability_matrix = np.ma.MaskedArray(data=np.full(self.grid.shape, 0, dtype=float), mask=True)

    def get_probability_matrix(self):
        return self.probability_matrix.copy()

    @classmethod
    def filter(cls, session, *args, **kwargs):
        instance = cls()
        taxon = session.query(Taxon).get(kwargs['taxon'])
        instance.logger.info('applying {} filter to taxon {}'.format(cls.__module__, taxon.taxon_key))

        kwargs['session'] = session
        kwargs['taxon'] = taxon
        probability = instance._filter(*args, **kwargs)

        # probability should either be  all masked or contain
        # only values 0->1:

        assert(
            probability is None
            or
            np.ma.all(probability.mask)
            or
            np.isnan(probability.max())
            or
            (probability.max() <= 1 and probability.min() >= 0)
        )

        return probability

    @functools.lru_cache(maxsize=None)
    def depth_probability(self, seafloor_depth, taxon_mindepth, taxon_maxdepth):
        """
        calculates probability of taxon in seafloor_depth of water based on a
        triangular distribution with maximum at 1/3 down

        currently used by depth filter

        parameters
        seafloor_depth of seafloor (in negative meters)
        taxon_mindepth of taxon (closer to surface, in negative meters)
        taxon_maxdepth of taxon (further from surface, in negative meters)

        """

        # short circuit easy answers:
        if seafloor_depth < taxon_maxdepth:
            return 1.0
        elif seafloor_depth > taxon_mindepth:
            return 0.0

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
