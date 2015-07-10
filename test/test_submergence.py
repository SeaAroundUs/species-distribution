import unittest2

import species_distribution.filters as filters


class TestHabitat(unittest2.TestCase):

    def test_equatorial_symmetric_parabola_fit(self):
        submergence_filter = filters.submergence.Filter()
        min_depth = -1
        max_depth = -10
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
        self.assertAlmostEqual(lower_f(0), -526.1, places=1)
        self.assertLess(mean_depth, upper_f(0))

    def test_400250_parabola_fit(self):
        # this taxa was producing inverted parabolas
        submergence_filter = filters.submergence.Filter()
        min_depth = -200
        max_depth = -1500
        lat_north = -23
        lat_south = -67
        upper_f, lower_f = submergence_filter.fit_parabolas(min_depth, max_depth, lat_north, lat_south)
        self.assertAlmostEqual(upper_f(0), -607.6, places=1)

    def test_500871_parabola_fit(self):
        submergence_filter = filters.submergence.Filter()
        min_depth = -10
        max_depth = -50
        mean_depth = -submergence_filter._geometric_mean((abs(min_depth), abs(max_depth)))
        lat_north = 65
        lat_south = 14
        upper_f, lower_f = submergence_filter.fit_parabolas(min_depth, max_depth, lat_north, lat_south)
        self.assertAlmostEqual(upper_f(0), -22.4, places=1)

    def test_690628_parabola_fit(self):
        # this taxa was producing crossing parabolas.  Still is.
        submergence_filter = filters.submergence.Filter()
        min_depth = -69
        max_depth = -108
        lat_north = 45
        lat_south = 20
        upper_f, lower_f = submergence_filter.fit_parabolas(min_depth, max_depth, lat_north, lat_south)
        self.assertAlmostEqual(upper_f(0), -157.7, places=1)
