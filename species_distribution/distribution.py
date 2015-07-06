import logging

import settings
import species_distribution.exceptions as exceptions
import species_distribution.filters as filters
import species_distribution.io as io
import species_distribution.utils as utils

logger = logging.getLogger(__name__)


def create_taxon_distribution(taxonkey):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    logger.info("working on taxon {}".format(taxonkey))

    try:

        matrices = [f(taxon=taxonkey) for f in (
            filters.polygon.Filter.filter,
            filters.fao.Filter.filter,
            filters.latitude.Filter.filter,
            filters.depth.Filter.filter,
            filters.habitat.Filter.filter,
            filters.submergence.Filter.filter,
        )]

        distribution_matrix = utils.combine_probability_matrices(matrices)

        # water_percentage = Grid().get_grid('PWater') / 100
        # distribution_matrix *= water_percentage

        if settings.DEBUG:
            for i, m in enumerate(matrices):
                fname = '{}-{}'.format(taxonkey, i)
                io.save_image(m, fname)

            fname = taxonkey
            io.save_image(distribution_matrix, fname, enhance=False)
        return distribution_matrix

    except exceptions.InvalidTaxonException as e:
        logger.warn("Invalid taxon {}. Error: {}".format(taxonkey, str(e)))
    except exceptions.NoPolygonException as e:
        logger.warn("No polygon exists for taxon {}".format(taxonkey))


def create_and_save_taxon(taxonkey, force=False):

    distribution = create_taxon_distribution(taxonkey)
    io.save_database(distribution, taxonkey)
    io.save_hdf5(distribution, taxonkey, force=force)
    logger.info('taxon {} complete'.format(taxonkey))
