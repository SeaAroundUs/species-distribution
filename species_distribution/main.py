""" Main module for running species_distribution """

# import concurrent.futures
from enum import Enum
import functools
import logging
import operator

import species_distribution.exceptions as exceptions
import species_distribution.io as io
from species_distribution.models.db import session
from species_distribution.models.taxa import TaxonPara
from species_distribution.models.world import Grid
import species_distribution.filters as filters


def configure_logging(level):
    logging.basicConfig(
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
        level=level)

logger = logging.getLogger(__name__)


class Season(Enum):
    ANNUAL = 0
    SUMMER = 1
    WINTER = 2


def combine_probability_matrices(matrices):
    """given a sequence of probability matrices, combine them into a
    single matrix and return it"""

    return functools.reduce(operator.mul, matrices)

def create_taxon_distribution(taxon, season=Season.ANNUAL):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    logger.info("working on taxon {}".format(taxon.taxonkey))
    try:

        matrices = (f(taxon) for f in (
            filters.polygon.filter,
            filters.fao.filter,
            filters.latitude.filter,
            filters.depth.filter,
        ))

        distribution_matrix = combine_probability_matrices(matrices)
        return distribution_matrix

    except exceptions.InvalidTaxonException as e:
        logger.warn("Invalid taxon {}. Error: {}".format(taxon, str(e)))
    except exceptions.NoPolygonException as e:
        logger.warn("No polygon exists for taxon {}".format(taxon))


def main(args):
    configure_logging(args.verbose and logging.DEBUG or logging.INFO)
    logger.info("starting distribution")

    sesh = session()
    grid = Grid()

    # get taxa
    if args.limit:
        taxa = sesh.query(TaxonPara).all()[0:args.limit]
    elif args.taxon:
        taxa = sesh.query(TaxonPara).filter_by(taxonkey=args.taxon).all()
    else:
        taxa = sesh.query(TaxonPara).all()

    logger.info("Found {} taxa".format(len(taxa)))

    for taxon in taxa:
        if not taxon:
            logger.critical("taxon is empty.  I don't know why.")
            continue

        if not args.force and '/taxa/' + str(taxon.taxonkey) in io.completed_taxon():
            logger.info('taxon {} exists in output, skipping it.  Use -f to force'.format(taxon.taxonkey))
            continue

        distribution = create_taxon_distribution(taxon, {'season': Season.ANNUAL})

        if distribution is None:
            logger.debug('empty distribution returned')
            continue

        io.save_hdf5(distribution, taxon, force=args.force)

        logger.info('taxon {} complete'.format(taxon.taxonkey))

    io.close()
    logger.info('distribution complete')
    logger.debug('grid cache usage: {}'.format(grid.get_grid.cache_info()))
