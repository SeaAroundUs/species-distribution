import unittest2

from species_distribution.filters.filter import BaseFilter


class TestFilters(unittest2.TestCase):

    def test_depth_probability_deep_water(self):
        f = BaseFilter()
        actual = f.depth_probability(-1000, -10, -100)
        expected = 1.0
        self.assertEqual(actual, expected)

    def test_depth_probability_shallow_water(self):
        f = BaseFilter()
        actual = f.depth_probability(-1, -10, -100)
        expected = 0.0
        self.assertEqual(actual, expected)

    def test_depth_probability_in_range(self):
        f = BaseFilter()
        actual = f.depth_probability(-40, -10, -100)
        # depth is right at peak of triangular distribution, so ratio of top triangle to entire triangle
        expected = (0.5 * 30 * 1) / (0.5 * 90 * 1)
        self.assertEqual(actual, expected)
