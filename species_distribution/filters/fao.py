import numpy as np

from species_distribution.filters.filter import Filter


class FAOFilter(Filter):

    def _filter(self, taxon):
        probability_matrix = self.get_probability_matrix()

        fao_grid = self.grid.get_grid('FAO')
        faos = taxon.faos

        mask = np.zeros(fao_grid.shape, dtype=np.bool)

        # flip on bits for cells with an ID in faos
        for fao in faos:
            mask |= fao_grid == fao

        probability_matrix[mask] = 1.0

        return probability_matrix


_f = FAOFilter()


def filter(*args):
    return _f.filter(*args)
