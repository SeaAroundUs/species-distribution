import unittest2

from species_distribution.models.db import session
from species_distribution.models.taxa import Taxon


class TestTaxa(unittest2.TestCase):

    def test_taxon_para(self):
        key = 100025
        taxon = session().query(Taxon).get(key)
        self.assertEqual(key, taxon.taxonkey)
