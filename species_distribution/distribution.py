import functools
import logging
import operator

from .models.db import Session
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
        with Session() as session:
            matrices = [f.filter(session, taxon=taxonkey) for f in _filters]

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

        return (taxonkey, distribution_matrix)

    except InvalidTaxonException as e:
        logger.warning("Invalid taxon {}. Error: {}".format(taxonkey, str(e)))
    except NoPolygonException as e:
        logger.warning("No polygon exists for taxon {}".format(taxonkey))


def save_database(taxon_key, matrix):

    if matrix is None or matrix.mask.all():
        logger.info("Calculated matrix for taxon {} was None or masked, not saving to DB".format(taxon_key))
    else:
        logger.info('saving {} to DB'.format(taxon_key))
        io.save_database(matrix, taxon_key)


def create_and_save_distribution(taxonkey, force=False):
    """convenient hook for recon code to make a single call to create and save distribution"""

    _, distribution = create_taxon_distribution(taxonkey)
    save_database(taxonkey, distribution)
