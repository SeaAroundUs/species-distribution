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
        return instance._filter(*args, **kwargs)
