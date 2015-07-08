import unittest2

import numpy as np

from species_distribution import distribution


class TestUtils(unittest2.TestCase):

    def test_combine_probability_matrices(self):
        m1 = np.ma.MaskedArray(np.full((2, 2), np.nan), mask=True)
        m2 = np.ma.MaskedArray(np.full((2, 2), np.nan), mask=True)

        m1[0, 0] = .5
        m2[0, 0] = .1
        m2[0, 1] = .1

        result = distribution.combine_probability_matrices((m1, m2))

        self.assertEqual(result[0, 0], 1)
        self.assertFalse(result[0, 1])
