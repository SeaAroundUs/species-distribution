import numpy as np

from species_distribution.filters.filter import BaseFilter
from species_distribution.models.taxa import TaxonHabitat


class Filter(BaseFilter):

    def _filter(self, taxon=None, session=None):
        """ probability generated according to taxon_habitat.latnorth and taxon_habitat.latsouth

        Divides the range into thirds.

        If the middle third straddles the equator,
        then distribution is a polygon with maximum probability in the middle third,
        linearly decreasing to zero at latnorth and latsouth

        Else, distribution is a symmetric triangular distribution with maximum
        at the range mean
        """

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxon_key)

        taxon_range = taxon_habitat.lat_north - taxon_habitat.lat_south
        taxon_mean = (taxon_habitat.lat_north + taxon_habitat.lat_south) / 2

        middle_third_north = taxon_habitat.lat_north - (taxon_range / 3)
        middle_third_south = taxon_habitat.lat_north - (2 * taxon_range / 3)

        equator_in_middle_third = middle_third_north > 0 and middle_third_south < 0

        if equator_in_middle_third:
            # polygon distribution
            x_points = (taxon_habitat.lat_south, middle_third_south, middle_third_north, taxon_habitat.lat_north)
            y_points = (0, 1, 1, 0)
        else:
            # triangle distribution
            x_points = (taxon_habitat.lat_south, taxon_mean, taxon_habitat.lat_north)
            y_points = (0, 1, 0)

        # get a 1-d longitudinal distribution for each regime
        latitudes = self.grid.latitude[:, 0]
        distribution1d = np.interp(latitudes, x_points, y_points)
        mask = distribution1d <= 0
        distribution1d = np.ma.MaskedArray(data=distribution1d)
        distribution1d.mask = mask

        probability_matrix = self.get_probability_matrix()

        # broadcast 1-d north-south distribution across grid
        probability_matrix[:] = distribution1d.reshape(distribution1d.shape[0], 1)

        return probability_matrix
