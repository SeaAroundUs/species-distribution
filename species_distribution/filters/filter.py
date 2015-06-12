import logging

import numpy as np

from species_distribution.models.world import Grid


class Filter():
    """ subclasses of Filter should define a _filter method
    which will be called by filter
    """
    def __init__(self):
        self.grid = Grid()
        self.logger = logging.getLogger(__name__)

    def get_probability_matrix(self):
        return np.ma.MaskedArray(data=np.full(self.grid.shape, np.nan, dtype=float), mask=True)

    def filter(self, *args, **kwargs):
        self.logger.debug('applying {}'.format(self.__class__.__name__))
        return self._filter(*args, **kwargs)
