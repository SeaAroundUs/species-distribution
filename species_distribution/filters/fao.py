import numpy as np

from species_distribution.filters.filter import BaseFilter
from species_distribution.models.taxa import TaxonHabitat


class Filter(BaseFilter):

    def _filter(self, taxon=None, session=None):

        probability_matrix = self.get_probability_matrix()

        fao_grid = self.grid.get_grid('fao_area_id')

        mask = np.zeros(fao_grid.shape, dtype=np.bool)

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxon_key)
        # flip on bits for cells with an ID in faos
        for fao in taxon_habitat.faos:
            mask |= fao_grid == fao

        probability_matrix[mask] = 1.0

        return probability_matrix
