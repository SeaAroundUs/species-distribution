import functools
import logging
import operator

from .exceptions import InvalidTaxonException, NoPolygonException
from . import filters
from . import sd_io as io
from . import settings
from .models.world import Grid

logger = logging.getLogger(__name__)


def combine_probability_matrices(matrices):
    """given a sequence of probability matrices, combine them into a
    single matrix with sum 1.0 and return it"""

    distribution = functools.reduce(operator.mul, matrices)
    # normalize
    return distribution / distribution.sum()


def threaded_create_taxon_distribution(taxon_key):
    result = create_taxon_distribution(taxon_key)
    return (taxon_key, result)


def create_taxon_distribution(taxonkey):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    logger.info("working on taxon {}".format(taxonkey))

    _filters = (
        filters.polygon,
        filters.fao,
        filters.latitude,
        filters.depth,
        filters.habitat,
        filters.submergence
    )

    try:
        matrices = [f.filter(taxon=taxonkey) for f in _filters]

        if settings.DEBUG:
            for i, m in enumerate(matrices):
                fname = '{}-{}-{}'.format(taxonkey, i, _filters[i].name)
                io.save_image(m, fname)


        matrices = list(filter(lambda x: x is not None and x.count() > 0, matrices))  # remove Nones
        distribution_matrix = combine_probability_matrices(matrices)

        if settings.DEBUG:
            io.save_image(distribution_matrix, taxonkey)

        water_percentage = Grid().get_grid('percent_water') / 100
        distribution_matrix *= water_percentage

        return distribution_matrix

    except InvalidTaxonException as e:
        logger.warn("Invalid taxon {}. Error: {}".format(taxonkey, str(e)))
    except NoPolygonException as e:
        logger.warn("No polygon exists for taxon {}".format(taxonkey))


def create_and_save_taxon(taxonkey, force=False):

    distribution = create_taxon_distribution(taxonkey)
    if distribution is not None:
        io.save_database(distribution, taxonkey)
        if settings.DEBUG:
            io.save_hdf5(distribution, taxonkey, force=force)
        logger.info('taxon {} complete'.format(taxonkey))
    else:
        logger.critical('nothing done for taxon {}'.format(taxonkey))
