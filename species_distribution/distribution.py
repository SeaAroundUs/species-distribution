import functools
import logging
import operator

import settings
from .exceptions import InvalidTaxonException, NoPolygonException
from .filters import filter, polygon, fao, latitude, depth, habitat, submergence
from . import io
from .models.world import Grid

logger = logging.getLogger(__name__)


def combine_probability_matrices(matrices):
    """given a sequence of probability matrices, combine them into a
    single matrix and return it"""

    distribution = functools.reduce(operator.mul, (matrix for matrix in matrices if matrix is not None))
    # normalize distribution
    return distribution / distribution.max()


def create_taxon_distribution(taxonkey):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    logger.info("working on taxon {}".format(taxonkey))

    _filters = (
        {'name': 'polygon', 'f': polygon.Filter.filter},
        {'name': 'fao', 'f': fao.Filter.filter},
        {'name': 'latitude', 'f': latitude.Filter.filter},
        {'name': 'depth', 'f': depth.Filter.filter},
        {'name': 'habitat', 'f': habitat.Filter.filter},
        {'name': 'submergence', 'f': submergence.Filter.filter},
    )

    try:
        matrices = [f['f'](taxon=taxonkey) for f in _filters]

        distribution_matrix = combine_probability_matrices(matrices)

        water_percentage = Grid().get_grid('p_water') / 100
        distribution_matrix *= water_percentage

        if settings.DEBUG:
            for i, m in enumerate(matrices):
                fname = '{}-{}-{}'.format(taxonkey, i, _filters[i]['name'])
                if m is not None:
                    io.save_image(m, fname)

            fname = taxonkey
            io.save_image(distribution_matrix, fname, enhance=False)
            logger.debug('grid cache usage: {}'.format(Grid().get_grid.cache_info()))
            logger.debug('filter cache usage: {}'.format(filter.BaseFilter.depth_probability.cache_info()))
        return distribution_matrix

    except InvalidTaxonException as e:
        logger.warn("Invalid taxon {}. Error: {}".format(taxonkey, str(e)))
    except NoPolygonException as e:
        logger.warn("No polygon exists for taxon {}".format(taxonkey))


def create_and_save_taxon(taxonkey, force=False):

    distribution = create_taxon_distribution(taxonkey)
    if distribution is not None:
        io.save_database(distribution, taxonkey)
        io.save_hdf5(distribution, taxonkey, force=force)
        logger.info('taxon {} complete'.format(taxonkey))
    else:
        logger.critical('nothing done for taxon {}'.format(taxonkey))
