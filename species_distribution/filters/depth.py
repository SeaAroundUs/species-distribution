import functools

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

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxon_key)
        probability_matrix = self.get_probability_matrix()

        #if taxon_habitat.max_depth == 9999:
        #    self.logger.debug('skipping depth filter for {} since max_depth==9999'.format(taxon.taxon_key))
        #    return

        if taxon_habitat.offshore == 0:
            self.logger.debug('skipping depth filter for {} since Offshore==0'.format(taxon.taxon_key))
            return

        if taxon.pelagic:
            self.logger.debug('skipping depth filter for pelagic taxon {}'.format(taxon.taxon_key))
            return

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        #mindepth = -taxon.min_depth
        #maxdepth = -taxon.max_depth

        # TODO: Check with Deng to make sure these figures from HI is also inverted like they currently are in master.taxon
        mindepth = -taxon_habitat.min_depth
        maxdepth = -taxon_habitat.max_depth

        world_depth = self.grid.get_grid('ele_avg')

        deep_mask = world_depth < maxdepth
        probability_matrix[deep_mask] = 1.0

        # find world depths in taxon range,
        # then broadcast results of depth_probability() to probability_matrix
        depths_in_range = np.arange(mindepth, maxdepth - 1, -1)
        world_depths_in_range = np.intersect1d(depths_in_range, world_depth)
        f = functools.partial(self.depth_probability, taxon_mindepth=mindepth, taxon_maxdepth=maxdepth)
        for depth in world_depths_in_range:
            probability_matrix[world_depth == depth] = f(depth)

        return probability_matrix
