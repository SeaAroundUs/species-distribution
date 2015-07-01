import unittest2

import species_distribution.filters as filters


class TestHabitat(unittest2.TestCase):

    def test_equatorial_symmetric_parabola_fit(self):
        submergence_filter = filters.submergence.Filter()
        min_depth = -1
        max_depth = -10
        mean_depth = -submergence_filter._geometric_mean((abs(min_depth), abs(max_depth)))
        lat_north = 10
        lat_south = -10
        upper_f, lower_f = submergence_filter.fit_parabolas(min_depth, max_depth, lat_north, lat_south)
        self.assertAlmostEqual(lower_f(0), max_depth)
        self.assertAlmostEqual(upper_f(0), mean_depth, places=1)
        self.assertAlmostEqual(upper_f(5), -3.2, places=1)
