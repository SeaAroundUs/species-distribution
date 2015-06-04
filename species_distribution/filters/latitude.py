import functools

import numpy as np

from species_distribution.filters.filter import Filter

class LatitudeFilter(Filter):

    def triangle_f(self, value, N=None):
        """returns probability at point value from triangular distribution
        with shape left, mode, right
        """
        mode = N / 2.0
        if value <= mode:
            """increasing leg of triangle"""
            return value / mode
        else:
            """decreasing leg of triangle"""
            return 1 - ((value - mode) / mode)

    def triangular_distribution(self, lat_n=None, lat_s=None):
        """returns a 1 dimensional symmetric triangular probability distribution
        from  lat1 to lat2, mapped to the regular grid, and N, the location at
        which to apply this distribution
        """

        # our lat grid runs from 90,-90, numpy.searchsorted wants it reversed
        lat = self.grid._lat[:,0].copy()
        lat.sort()

        # find array indexes of range
        N_s = np.searchsorted(lat, lat_s, side='left')
        N_n = np.searchsorted(lat, lat_n, side='right')

        N = N_n - N_s

        f = functools.partial(self.triangle_f, N=N)
        points = np.array(list(map(f, range(N))))
        # return the index in the original sort order
        return points, len(lat) - N_n


    def filter(self, taxon):
        self.logger.debug('applying latitude filter')
        if taxon.latsouth >= 0 or taxon.latnorth <= 0:
            # taxon is contained in N or S hemisphere
            arr, N = self.triangular_distribution(taxon.latnorth, taxon.latsouth)
            M = N + len(arr)
            y_len = self.probability_matrix.shape[1]
            self.probability_matrix[N:M] = np.tile(arr, (y_len, 1)).transpose()
        else:
            # taxon straddles equator

            # create a mask index array of values meeting the criteria
            # and set probability value of those cells to 1
            mask = (self.grid._lat <= taxon.latnorth) & (self.grid._lat >= taxon.latsouth)
            self.probability_matrix[mask] = 1.0

        return self.probability_matrix


def filter(*args):
    f = LatitudeFilter()
    return f.filter(*args)
