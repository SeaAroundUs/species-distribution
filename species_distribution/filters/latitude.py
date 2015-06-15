import numpy as np

from species_distribution.filters.filter import BaseFilter


class Filter(BaseFilter):

    def _filter(self, taxon):
        """ probability generated according to taxon.latnorth and taxon.latsouth

        Divides the range into thirds.

        If the middle third straddles the equator,
        then distribution is a polygon with maximum probability in the middle third,
        linearly decreasing to zero at latnorth and latsouth

        Else, distribution is a symmetric triangular distribution with maximum
        at the range mean
        """

        taxon_range = taxon.latnorth - taxon.latsouth
        taxon_mean = (taxon.latnorth + taxon.latsouth) / 2
        middle_third_north = taxon.latnorth - (taxon_range / 3)
        middle_third_south = taxon.latnorth - (2 * taxon_range / 3)
        equator_in_middle_third = middle_third_north > 0 and middle_third_south < 0

        # get a 1-d longitudinal distribution for each regime

        latitudes = self.grid._lat[:, 0]

        if equator_in_middle_third:
            # polygon distribution
            x_points = (taxon.latsouth, middle_third_south, middle_third_north, taxon.latnorth)
            y_points = (0, 1, 1, 0)
        else:
            # triangle distribution
            x_points = (taxon.latsouth, taxon_mean, taxon.latnorth)
            y_points = (0, 1, 0)

        distribution1d = np.interp(latitudes, x_points, y_points)
        mask = distribution1d[distribution1d <= 0]
        distribution1d = np.ma.MaskedArray(data=distribution1d)
        distribution1d.mask = mask

        probability_matrix = self.get_probability_matrix()

        # broadcast 1-d north-south distribution across grid
        probability_matrix[:] = distribution1d.reshape(distribution1d.shape[0], 1)

        return probability_matrix
