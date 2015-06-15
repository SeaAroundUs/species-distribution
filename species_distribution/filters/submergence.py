import numpy as np

from species_distribution.filters.filter import BaseFilter
from species_distribution.models.world import Grid


class Filter(BaseFilter):

    def _filter(self, taxon):

        probability_matrix = self.get_probability_matrix()
        grid = Grid()
        return probability_matrix
