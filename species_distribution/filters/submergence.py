import numpy as np
from .filter import BaseFilter


class Filter(BaseFilter):
    """ Submergence Filter
    """

    def _filter(self, taxon):

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        world_depth = self.grid.get_grid('EleAvg')

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        # get polygon distribution to reduce work done here
        polygon_distribution = taxon.polygon_matrix  # or PolygonFilter.filter(taxon)
        mask = (world_depth > mindepth) | (world_depth >= 0) | polygon_distribution.mask

        probability_matrix = self.get_probability_matrix()

        # iterate over the valid values
        for i, j in np.ndindex(probability_matrix.shape):
            if mask[i, j]:
                continue

            seafloor_depth = world_depth[i, j]
            probability = self.depth_probability(seafloor_depth, mindepth, maxdepth)
            probability_matrix[i, j] = probability

        return probability_matrix
