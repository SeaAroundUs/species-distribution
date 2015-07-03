import numpy as np

from species_distribution.filters.filter import BaseFilter


class Filter(BaseFilter):

    def _filter(self, taxon=None, session=None):

        probability_matrix = self.get_probability_matrix()

        fao_grid = self.grid.get_grid('FAO')

        mask = np.zeros(fao_grid.shape, dtype=np.bool)

        # flip on bits for cells with an ID in faos
        for fao in taxon.faos:
            mask |= fao_grid == fao

        probability_matrix[mask] = 1.0

        return probability_matrix
