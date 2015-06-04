import logging

import numpy as np

from species_distribution.filters.filter import Filter

logger = logging.getLogger(__name__)


class FAOFilter(Filter):

    def filter(self, taxon):
        logger.debug('applying fao filter')

        fao_grid = self.grid.get_grid('FAO')
        faos = taxon.faos

        mask = np.zeros(fao_grid.shape, dtype=np.bool)

        # flip on bits for cells with an ID in faos
        for fao in faos:
            mask |= fao_grid == fao

        self.probability_matrix[mask] = 1.0

        return self.probability_matrix


def filter(*args):
    f = FAOFilter()
    return f.filter(*args)
