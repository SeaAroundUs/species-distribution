import math

import numpy as np

from .filter import BaseFilter


class Filter(BaseFilter):
    """ Submergence Filter
    """

    def _geometric_mean(self, a):

        sum_of_logs = sum([math.log(x, 10) for x in a])
        return 10 ** (sum_of_logs / len(a))

    def _filter(self, taxon):

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        world_depth = self.grid.get_grid('EleMin')

        min_depth = -taxon.mindepth
        max_depth = -taxon.maxdepth

        # get polygon distribution to reduce work done here
        # polygon_distribution = taxon.polygon_matrix  # or PolygonFilter.filter(taxon)
        # mask = (world_depth > min_depth)

        probability_matrix = self.get_probability_matrix()

        # define upper and lower parabolas as defined in section 6 of catch reconstruction
        # document http://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/#_Toc421534359

        mean_depth = -self._geometric_mean((taxon.mindepth, taxon.maxdepth))

        # depending on relationship of latnorth/latsouth and the equator, define different upper
        # and lower parabolas according to business rules.  These are modelled by each branch
        # as p_high (upper parabola) and p_low (lower parabola)

        if (taxon.latnorth - taxon.latsouth) > 0 and taxon.latnorth <= 60 and taxon.latsouth >= -60:
            # latitude range is in one hemisphere, and within 60/-60
            # section b) of documentation

            x_high = (60, taxon.latnorth, -60)
            y_high = (0, min_depth, 0)

            x_low = (60, taxon.latsouth, -60)
            y_low = (mean_depth, max_depth, mean_depth)

            p_high = np.poly1d(np.polyfit(x_high, y_high, 2))
            p_low = np.poly1d(np.polyfit(x_low, y_low, 2))

        elif taxon.latnorth > 0 and taxon.latnorth < 60 and taxon.latsouth < 0 and taxon.latsouth > -60:
            # latitude range spans equator, and within 60/-60
            # section c) of documentation

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

            if seafloor_depth < submergence_min_depth:
                probability = self.depth_probability(seafloor_depth, submergence_min_depth, submergence_max_depth)
                # self.logger.debug('{} {} {}'.format(seafloor_depth, submergence_min_depth, submergence_max_depth))
                probability_matrix[i, j] = probability

        return probability_matrix
