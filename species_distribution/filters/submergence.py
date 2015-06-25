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

        min_depth = -taxon.mindepth
        max_depth = -taxon.maxdepth

        # get polygon distribution to reduce work done here
        # polygon_distribution = taxon.polygon_matrix  # or PolygonFilter.filter(taxon)
        mask = (world_depth > min_depth)

        probability_matrix = self.get_probability_matrix()

        # define upper and lower parabolas as defined in section 6 of catch reconstruction
        # document http://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/#_Toc421534359

        mean_depth = (min_depth + max_depth) / 2

        if taxon.latnorth > 0 and taxon.latsouth < 0:
            # latitude range spans equator

            x = [60, 0, -60]

            y_high = [0, mean_depth, 0]
            y_low = [mean_depth, max_depth, mean_depth]

            p_high = np.poly1d(np.polyfit(x, y_high, 2))
            p_low = np.poly1d(np.polyfit(x, y_low, 2))

            # iterate over the valid values
            for i, j in np.ndindex(probability_matrix.shape):
                # if mask[i, j]:
                #     continue

                submergence_min_depth = p_high(self.grid.latitude[i, 0])
                submergence_max_depth = p_low(self.grid.latitude[i, 0])

                seafloor_depth = world_depth[i, j]

                probability = self.depth_probability(seafloor_depth, submergence_min_depth, submergence_max_depth)
                # self.logger.debug('{} {} {}'.format(seafloor_depth, submergence_min_depth, submergence_max_depth))
                probability_matrix[i, j] = probability

        return probability_matrix
