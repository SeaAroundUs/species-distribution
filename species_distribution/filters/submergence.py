import math
import sys

import numpy as np

from .filter import BaseFilter
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

    Depth gradients are defined usi ng a parabolic function of the form: y = ax2
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
        # and lower parabolas according to business rules.  The 3 points defining each parabola are
        # defined by each branch then modeled as p_high (upper parabola) and p_low (lower parabola)

        if lat_north > 0 and lat_north < 60 and lat_south < 0 and lat_south > -60:
            # latitude range spans equator, and within 60/-60
            # section c)
            x_high = (60, lat_north, -60)
            y_high = (0, min_depth, 0)

            x_low = (60, 0, -60)
            y_low = (mean_depth, max_depth, mean_depth)

        elif (lat_north > 0 and lat_north <= 60) or (lat_south <= 0 and lat_south >= -60):
            # latitude range is in one hemisphere, and within 60/-60
            x_high = [60, lat_north, -60]
            y_high = [0, min_depth, 0]

            x_low = [60, lat_south, -60]
            y_low = [mean_depth, max_depth, mean_depth]

        elif lat_north > 60 or lat_south < -60:
            # section d) of documentation

            x_high = [lat_north, 60, -60]
            y_high = [0, min_depth, min_depth]

            x_low = [lat_south, 60, -60]
            y_low = [max_depth, mean_depth, mean_depth]

        else:
            raise Exception('no submergence rules for lat_north: {} lat_south: {}'.format(lat_north, lat_south))

        p_high = np.poly1d(np.polyfit(x_high, y_high, 2))
        p_low = np.poly1d(np.polyfit(x_low, y_low, 2))

        return p_high, p_low

    def _plot_parabolas(self, p_high, p_low, min_depth, max_depth, lat_north, lat_south, taxon_key):
        """ writes out a PNG plot of the calculated parabolas and the parameters used
        to generate them"""
        import matplotlib.pyplot as plt
        import os
        x = np.arange(60,-60,-.1)
        plt.plot(x, p_high(x))
        plt.plot(x, p_low(x))
        plt.axhline(min_depth)
        plt.axhline(max_depth)
        plt.axvline(lat_north)
        plt.axvline(lat_south)
        plt.savefig(os.path.join(settings.PNG_DIR, '{}-submergence-parabolas.png'.format(taxon_key)))

    def _filter(self, taxon):

        # min and max are inverted between taxon and world
        # world goes from surface at EleMax: 0 to EleMin: -N at depth
        # taxon goes from surface mindepth 0 to maxdepth: N at depth

        # world_min_depth = self.grid.get_grid('EleMax')
        world_max_depth = self.grid.get_grid('EleMin')

        min_depth = -taxon.mindepth
        max_depth = -taxon.maxdepth

        probability_matrix = self.get_probability_matrix()

        p_high, p_low = self.fit_parabolas(min_depth, max_depth, taxon.latnorth, taxon.latsouth)

        if settings.DEBUG:
            self._plot_parabolas(p_high, p_low, min_depth, max_depth, taxon.latnorth, taxon.latsouth, taxon.taxonkey)

        # submergence is constant poleward of 60/-60/latnorth/latsouth
        latitudes = np.clip(self.grid.latitude[:, 0], min(taxon.latsouth, -60), max(60, taxon.latnorth))

        for i, j in np.ndindex(probability_matrix.shape):
            if (hasattr(taxon, 'polygon_matrix') and taxon.polygon_matrix.mask[i, j]):
                continue

            latitude = latitudes[i]

            submergence_min_depth = p_high(latitude)
            submergence_max_depth = p_low(latitude)

            if world_max_depth[i, j] < submergence_min_depth:
                probability = self.depth_probability(world_max_depth[i, j], submergence_min_depth, submergence_max_depth)
                probability_matrix[i, j] = probability

        return probability_matrix
