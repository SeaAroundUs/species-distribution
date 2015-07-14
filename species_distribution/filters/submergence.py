import math
import sys

import numpy as np

from .filter import BaseFilter
from species_distribution.models.taxa import TaxonHabitat
import settings


class Filter(BaseFilter):
    """ Submergence Filter

    Primary documentation source:
    http://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/#_Toc421534359

    Additional documentation from email with Deng Palomares <m.palomares@fisheries.ubc.ca>
    June 24, 2015:


    What the filter should do: refines the distribution (resulting from the
    application of the earlier filters) to mimic the distribution gradient
    correlated with depth (shaves off cells which fall outside of the
    established depth gradients)

    Depth gradients are defined using a parabolic function of the form: y = ax2
    + bx + c, where Y is depth and X is latitude

    Two parabolas are needed, one defines the shallow depth gradient and the
    other defines the deeper depth gradient

    Parameters identified are:

    1)  Dhigh=shallow depth limit (minimum depth or Dmin in the TaxonNom table);

    2)  Dlow=deep depth limit (maximum depth or Dmax in the TaxonNom table);

    3)  Lhigh=poleward limit of the latitudinal range (Northern latitudinal
    limit in the TaxonNom table);

    4)  Llow=lower latitudinal limit of the range (Southern latitudinal limit in
    the TaxonNom table).

    The following assumptions are made:

    1)  Maximum depths are assumed not to change poleward of 60°N and 60°S;

    2)  Dhigh corresponds to Lhigh and Dlow to Llow;

    3)  Parabolas are drawn using three points (see figures a-c in the methods
    page http://www.seaaroundus.org/catch-reconstruction-and-allocation-
    methods/#_Toc421534359);

    a.   The parabola describing the shallow depth gradient is less concave than
    that of the deeper depth gradient by setting the geometric mean depth
    (transforming Dmax and Dmin into logs before taking the average value, then
    taking the antilog of the average value) as its deepest depth;

    b.  If the N/S limits are not higher than 60°N or lower than 60°S (see case
    in figure a), then the parabola describing the shallow depth gradient is
    obtained using the following three points: Dat60N=0, Dat60S=0, and
    DatNlimit=Dmin. The parabola describing the deep depth gradient is obtained
    using the following three points: Dat60N=10^( (logDmin+logDmax)/2),
    DatSlimit=Dmax, Dat60S=10^((logDmin+logDmax)/2).

    c.   If the northern latitudinal limit is in the northern hemisphere and the
    southern latitudinal limit is in the southern hemisphere (not higher than
    60°N or lower than 60°S), the shallow depth gradient parabola is as in (b)
    above and the deep depth gradient parabola is obtained using the following
    three points: Dmax is positioned at the equator (figure b) and Dat60N and
    Dat60S are as in (b) above;

    d.  If the computed parabolas intercept D=0 at latitudes higher than 60°N
    and/or lower than 60°S (figure c), then, the shallow depth gradient parabola
    is obtained using the following three points: Dat60N=Dmin, Dat60S=Dmin, and
    DatNlimit=0; and the deep depth gradient parabola is obtained using the
    following three points: Dat60N and Dat60S = 10^( (logDmin+logDmax)/2), and
    DatSlimit=Dmax.

    The resulting depth at latitude parabolas define an area inside the shallow
    and deep gradient lines where the species is most likely to be found. This
    is then used to “shave off” cells that do not fall within the defined area.

    """

    def _geometric_mean(self, a):
        """ a should be a sequence of numbers greater than 0 """
        try:
            sum_of_logs = sum((math.log(x, 10) for x in a))
        except ValueError:
            self.logger.critical('unable to take log of negative number in {}'.format(str(a)))
            raise
        return 10 ** (sum_of_logs / len(a))

    def get_scenario(self, lat_north, lat_south):
        if lat_north >= 0 and lat_south >= 0:
            return 1
        if lat_north <= 0 and lat_south <= 0:
            return 2
        if lat_north >= 0 and lat_south <= 0 and abs(lat_north) > abs(lat_south):
            return 3
        if lat_north >= 0 and lat_south <= 0 and abs(lat_north) < abs(lat_south):
            return 4
        if lat_north >= 0 and lat_south >= 0 and abs(lat_north) == abs(lat_south):
            return 5

    def fit_parabolas(self, min_depth, max_depth, lat_north, lat_south):
        """ returns a tuple of two functions (upper, lower) which are fitted
        polynomials representing the upper and lower parabolas defined by the
        submergence model
        """

        # geometric mean requires values > 0, so the data is ever so slightly tweaked to handle
        # depth values of 0
        if min_depth == 0:
            min_depth += sys.float_info.epsilon
        mean_depth = -self._geometric_mean((abs(min_depth), abs(max_depth)))

        # depending on relationship of latnorth/latsouth and the equator, define different upper
        # and lower parabolas according to business rules.  The 3 or 4 points defining each parabola are
        # defined by each branch then modeled as p_high (upper parabola) and p_low (lower parabola)

        scenario = self.get_scenario(lat_north, lat_south)

        if lat_north >= 60 or lat_north <= -60 or lat_south >= 60 or lat_south <= -60:
            # Case 1, not bounded by 60/-60
            if scenario == 1:
                x_high = (60, 0, -60)
                y_high = (min_depth, mean_depth, mean_depth)

                x_low = (60, lat_south, -lat_south, -60)
                y_low = (mean_depth, max_depth, max_depth, mean_depth)

            elif scenario == 2:
                x_high = (60, 0, -60)
                y_high = (min_depth, mean_depth, mean_depth)

                x_low = (60, lat_north, -lat_north, -60)
                y_low = (mean_depth, max_depth, max_depth, mean_depth)

            elif scenario == 3:
                x_high = (60, 0, -60)
                y_high = (min_depth, mean_depth, mean_depth)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

            elif scenario == 4:
                x_high = (60, 0, -60)
                y_high = (min_depth, min_depth, mean_depth)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

            elif scenario == 5:
                x_high = (60, 0, -60)
                y_high = (min_depth, mean_depth, mean_depth)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

        else:
            # Case 2, bounded by 60/-60
            if scenario == 1:
                x_high = (60, lat_north, -lat_north, -60)
                y_high = (0, min_depth, min_depth, 0)

                x_low = (60, lat_south, -lat_south, -60)
                y_low = (mean_depth, max_depth, max_depth, mean_depth)

            elif scenario == 2:
                x_high = (60, lat_south, -lat_south, -60)
                y_high = (0, min_depth, min_depth, 0)

                x_low = (60, lat_north, -lat_north, -60)
                y_low = (mean_depth, max_depth, max_depth, mean_depth)

            elif scenario == 3:
                x_high = (60, lat_north, -lat_north, -60)
                y_high = (0, min_depth, min_depth, 0)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

            elif scenario == 4:
                x_high = (60, lat_south, -lat_south, -60)
                y_high = (0, min_depth, min_depth, 0)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

            elif scenario == 5:
                x_high = (60, lat_north, -lat_north, -60)
                y_high = (0, min_depth, min_depth, 0)

                x_low = (60, 0, -60)
                y_low = (mean_depth, max_depth, mean_depth)

        p_high = np.poly1d(np.polyfit(x_high, y_high, 2))
        p_low = np.poly1d(np.polyfit(x_low, y_low, 2))

        return p_high, p_low

    def _plot_parabolas(self, p_high, p_low, min_depth, max_depth, lat_north, lat_south, taxon_key):
        """ writes out a PNG plot of the calculated parabolas and the parameters used
        to generate them"""
        import matplotlib.pyplot as plt
        import os
        x = np.arange(60,-60,-.1)
        plt.cla()  # clear preexisting plots
        plt.plot(x, p_high(x))
        plt.plot(x, p_low(x))
        plt.axhline(min_depth)
        plt.axhline(max_depth)
        plt.axvline(lat_north)
        plt.axvline(lat_south)

        if not os.path.isdir(settings.PNG_DIR):
            os.makedirs(settings.PNG_DIR)

        plt.savefig(os.path.join(settings.PNG_DIR, '{}-submergence-parabolas.png'.format(taxon_key)))

    def _grid_parabola(self, f):
        """ given a function f which defines a fitted parabola,
        return a Grid shaped array with that parabola applied
        to 60/-60, and constant across longitudes """
        # submergence is constant poleward of 60/-60
        latitudes = np.clip(self.grid.latitude[:, 0], -60, 60)
        y = f(latitudes)

        matrix = self.get_probability_matrix()
        # broadcast 1-D array across longitudes:
        matrix[:] = y.reshape(y.shape[0], 1)   # pivot
        return matrix

    def _filter(self, taxon=None, session=None):

        taxon_habitat = session.query(TaxonHabitat).get(taxon.taxon_key)

        if taxon_habitat.intertidal:
            self.logger.debug('Skipping submergence filter for intertidal taxon {}'.format(taxon.taxon_key))
            return

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        # world_min_depth = self.grid.get_grid('EleMax')
        ocean_depth = self.grid.get_grid('ele_min')
        percent_water = self.grid.get_grid('p_water')

        min_depth = -taxon.min_depth
        max_depth = -taxon.max_depth

        if max_depth == 9999 or abs(taxon.lat_north) == 90 or abs(taxon.lat_south) == 90:
            # short circuit, won't do submergence with missing data
            return

        p_high, p_low = self.fit_parabolas(min_depth, max_depth, taxon.lat_north, taxon.lat_south)

        if settings.DEBUG:
            self._plot_parabolas(p_high, p_low, min_depth, max_depth, taxon.lat_north, taxon.lat_south, taxon.taxon_key)

        p_high_array = self._grid_parabola(p_high)
        p_low_array = self._grid_parabola(p_low)

        # define a mask with which to set cell values at 1 (or default to masked)
        # based on submergence rules
        mask = (
            ((percent_water < 100) & (ocean_depth < p_high_array))
            |
            ((ocean_depth <= p_high_array) & (ocean_depth >= p_low_array))
        )
        probability_matrix = self.get_probability_matrix()
        probability_matrix[mask] = 1

        return probability_matrix
