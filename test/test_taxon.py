import unittest2

from species_distribution.models.db import Session
from species_distribution.models.taxa import Taxon


class TestTaxa(unittest2.TestCase):

    def test_taxon(self):
        key = 100025
        with Session() as session:
            taxon = session.query(Taxon).get(key)
            self.assertEqual(key, taxon.taxon_key)
