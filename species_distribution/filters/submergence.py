import math

import numpy as np

from .filter import BaseFilter


class Filter(BaseFilter):
    """ Submergence Filter

    Documentation from email with Deng Palomares <m.palomares@fisheries.ubc.ca>
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
        # and lower parabolas according to business rules.  The 3 points defining each parabola are
        # defined by each branch then modeled as p_high (upper parabola) and p_low (lower parabola)

        if (taxon.latnorth - taxon.latsouth) > 0 and taxon.latnorth <= 60 and taxon.latsouth >= -60:
            # latitude range is in one hemisphere, and within 60/-60
            # section b) of documentation

            x_high = (60, taxon.latnorth, -60)
            y_high = (0, min_depth, 0)

            x_low = (60, taxon.latsouth, -60)
            y_low = (mean_depth, max_depth, mean_depth)

        elif taxon.latnorth > 0 and taxon.latnorth < 60 and taxon.latsouth < 0 and taxon.latsouth > -60:
            # latitude range spans equator, and within 60/-60
            # section c) of documentation

            x_high = [60, taxon.latnorth, -60]
            y_high = [0, mean_depth, 0]

            x_low = [60, 0, -60]
            y_low = [mean_depth, max_depth, mean_depth]

        elif taxon.latnorth > 60 or taxon.latsouth < -60:
            # section d) of documentation

            x_high = [taxon.latnorth, 60, -60]
            y_high = [0, min_depth, min_depth]

            x_low = [taxon.latsouth, 60, -60]
            y_low = [max_depth, mean_depth, mean_depth]

        else:
            raise Exception('no submergence rules for latnorth: {} latsouth: {}'.format(taxon.latnorth, taxon.latsouth))

        p_high = np.poly1d(np.polyfit(x_high, y_high, 2))
        p_low = np.poly1d(np.polyfit(x_low, y_low, 2))

        for i, j in np.ndindex(probability_matrix.shape):

            # submergence is constant poleward of 60/-60
            latitude = np.clip(self.grid.latitude[i, 0], -60, 60)

            submergence_min_depth = p_high(latitude)
            submergence_max_depth = p_low(latitude)

            seafloor_depth = world_depth[i, j]

            if seafloor_depth < submergence_min_depth:
                probability = self.depth_probability(seafloor_depth, submergence_min_depth, submergence_max_depth)
                probability_matrix[i, j] = probability

        return probability_matrix
