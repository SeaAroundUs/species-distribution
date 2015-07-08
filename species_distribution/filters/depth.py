import numpy as np

from .filter import BaseFilter
from species_distribution.models.taxa import TaxonHabitat


class Filter(BaseFilter):
    """ Depth Filter

    probability_matrix values are defined where taxon min and max depth
    fall within the min and max depth of the cell.  Value is
    proportional to the amount falling within the scalene triangle
    distribution

    This filter is skipped if the species is coastal (Offshore = 0)
    """

    def _filter(self, taxon=None, session=None):

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxonkey)

        if taxon_habitat.Offshore == 0:
            self.logger.debug('skipping depth filter for {} since Offshore==0'.format(taxon.taxonkey))
            return

        mindepth = -taxon.mindepth
        maxdepth = -taxon.maxdepth

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        world_depth = self.grid.get_grid('EleAvg')

        mask = (world_depth > mindepth) | (world_depth >= 0)

        probability_matrix = self.get_probability_matrix()

        # iterate over the valid values
        for i, j in np.ndindex(probability_matrix.shape):
            if mask[i, j]:
                continue

            seafloor_depth = world_depth[i, j]

            P = self.depth_probability(seafloor_depth, mindepth, maxdepth)
            probability_matrix[i, j] = P

        return probability_matrix
