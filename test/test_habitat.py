import unittest2

import numpy as np

from species_distribution import filters


class TestHabitat(unittest2.TestCase):

    def test_membership_function(self):
        f = filters.habitat.MembershipFunction([25, 50, 100, 150])

        values = f.values(0)
        self.assertAlmostEqual(values[0], 1)
        self.assertAlmostEqual(values[1], 0)
        self.assertAlmostEqual(values[2], 0)

        values = f.values(125)
        self.assertAlmostEqual(values[0], 0)
        self.assertAlmostEqual(values[1], .5)
        self.assertAlmostEqual(values[2], .5)

        values = f.values(9999)
        self.assertAlmostEqual(values[0], 0)
        self.assertAlmostEqual(values[1], 0)
        self.assertAlmostEqual(values[2], 1)
