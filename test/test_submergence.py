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
        self.assertAlmostEqual(upper_f(lat_north), min_depth)
        self.assertAlmostEqual(upper_f(5), -1.02, places=1)

    def test_100036_parabola_fit(self):
        # this taxa was producing inverted parabolas
        submergence_filter = filters.submergence.Filter()
        min_depth = -1
        max_depth = -300
        mean_depth = -submergence_filter._geometric_mean((abs(min_depth), abs(max_depth)))
        lat_north = 90
        lat_south = -90
        upper_f, lower_f = submergence_filter.fit_parabolas(min_depth, max_depth, lat_north, lat_south)
        self.assertAlmostEqual(lower_f(0), max_depth)
        self.assertLess(mean_depth, upper_f(0))
