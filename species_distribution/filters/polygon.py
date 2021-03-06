"""Filters which accept a distribution matrix, and return a modified matrix"""

from ..filters.filter import BaseFilter
from ..models.taxa import polygon_cells_for_taxon


class Filter(BaseFilter):

    def _filter(self, taxon=None, session=None):
        """ sets probability to 1.0 for every grid cell which intersects
        the taxon distribution defined in the distribution geometries.
        Returns distribution_matrix"""

        probability_matrix = self.get_probability_matrix()

        cells = polygon_cells_for_taxon(taxon.taxon_key)

        # use numpy indexing to set all records of (row,col) to 1
        indexes = list(zip(*cells))
        probability_matrix[indexes[0], indexes[1]] = 1.0

        return probability_matrix
