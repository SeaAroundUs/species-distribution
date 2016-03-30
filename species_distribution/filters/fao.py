from species_distribution.filters.filter import BaseFilter
from species_distribution.models.taxa import fao_cells_for_taxon
from species_distribution.models.world import Grid


class Filter(BaseFilter):

    def _filter(self, taxon=None, session=None):

        probability_matrix = self.get_probability_matrix()

        cells = fao_cells_for_taxon(taxon.taxon_key)
        indexes = list(zip(*cells))
        probability_matrix[indexes[0], indexes[1]] = indexes[2]

        return probability_matrix
