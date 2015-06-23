import unittest2

from species_distribution.models.db import session
import species_distribution.filters as filters
from species_distribution.models.taxa import Taxon


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

    def test_filter(self):

        key = 690690
        taxon = session().query(Taxon).filter_by(taxonkey=key).one()

        distribution = filters.habitat.Filter.filter(taxon)
        self.assertEqual(distribution.shape, (360, 720))

    def test_frustrum_kernel(self):
        r1 = 20
        r2 = 5
        kernel = filters.habitat.conical_frustrum_kernel(r1, r2)
        self.assertEqual(kernel.shape, (r1 * 2 + 1, r1 * 2 + 1))
        self.assertFalse(kernel[0, 0], 'corner value should be masked')
        self.assertEqual(kernel[r1, r1], 1, 'center value is not 1')
        self.assertEqual(kernel[r1 + r2, r1], 1, 'value at r2 is not 1')
        self.assertTrue(kernel[r1 + r2 + 1, r1] < 1, 'value at r2 is not less than 1')
