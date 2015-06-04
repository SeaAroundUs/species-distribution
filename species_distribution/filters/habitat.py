import logging

from species_distribution.models.db import session
from species_distribution.models.taxa import TaxonHabitat
from species_distribution.filters.filter import Filter


class HabitatFilter(Filter):

    def filter(self, taxon, habitat):
        raise NotImplementedError

        logging.debug('applying habitat filter')

        sesh = session()

        habitat = sesh.query(TaxonHabitat).get(taxon.taxonkey)

        return self.probability_matrix


def filter(*args):
    f = HabitatFilter()
    return f.filter(*args)
