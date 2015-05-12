import unittest2

from species_distribution.models.db import session
from species_distribution.models.taxa import  TaxonPara


class TestTaxa(unittest2.TestCase):

    # def test_taxa(self):
    #     key = 100000
    #     taxon = session().query(Taxon).get(key)
    #     self.assertEqual(key, taxon.key)

    def test_taxon_para(self):
        key = 100025
        taxon = session().query(TaxonPara).get(key)
        self.assertEqual(key, taxon.taxonkey)
