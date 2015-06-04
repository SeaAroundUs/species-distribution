import logging

from species_distribution.filters.filter import Filter


class LatitudeFilter(Filter):

    def filter(self, taxon):
        logging.debug('applying latitude filter')

        # create a mask index array of values meeting the criteria
        # and set probability value of those cells to 1
        mask = (self.grid._lat <= taxon.latnorth) & (self.grid._lat >= taxon.latsouth)
        self.probability_matrix[mask] = 1.0
        return self.probability_matrix


def filter(*args):
    f = LatitudeFilter()
    return f.filter(*args)
