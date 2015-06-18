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

        filter = filters.habitat.Filter()

        key = 690690
        taxon = session().query(Taxon).filter_by(taxonkey=key).one()

        probability_distribution = filter.filter(taxon)
        self.assertEqual(probability_distribution.shape, (360, 720))
