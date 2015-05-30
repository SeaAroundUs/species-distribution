import logging

from species_distribution.filters.filter import Filter

logger = logging.getLogger(__name__)


class FAOFilter(Filter):

    def filter(self, taxon):
        logger.debug('applying fao filter')

        fao_grid = self.grid.get_grid('FAO')
        faos = taxon.faos

        w, h = self.grid.shape

        for j in range(h):
            for i in range(w):
                if fao_grid[i][j] in faos:
                    self.probability_matrix[i][j] = 1

        return self.probability_matrix


def filter(*args):
    f = FAOFilter()
    return f.filter(*args)
