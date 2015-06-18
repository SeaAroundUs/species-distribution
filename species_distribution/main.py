""" Main module for running species_distribution """

from enum import Enum
import logging
import signal

import settings
import species_distribution.exceptions as exceptions
import species_distribution.io as io
from species_distribution.models.db import session
from species_distribution.models.taxa import Taxon, TaxonDistribution
from species_distribution.models.world import Grid
import species_distribution.filters as filters
import species_distribution.utils as utils

STOP = False


def configure_logging(level):
    logging.basicConfig(
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
        level=level)

logger = logging.getLogger(__name__)


def signal_handler(*args):
    global STOP
    logger.warning("SIGINT caught, raising STOP flag")
    STOP = True

signal.signal(signal.SIGINT, signal_handler)


class Season(Enum):
    ANNUAL = 0
    SUMMER = 1
    WINTER = 2


def create_taxon_distribution(taxon, season=Season.ANNUAL):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    logger.info("working on taxon {}".format(taxon.taxonkey))
    try:

        matrices = [f(taxon) for f in (
            filters.polygon.Filter.filter,
            filters.fao.Filter.filter,
            filters.latitude.Filter.filter,
            filters.depth.Filter.filter,
            filters.habitat.Filter.filter,
            # filters.submergence.Filter.filter,
        )]

        distribution_matrix = utils.combine_probability_matrices(matrices)

        water_percentage = Grid().get_grid('PWater') / 100
        distribution_matrix *= water_percentage

        if settings.DEBUG:
            for i, m in enumerate(matrices):
                fname = '{}-{}'.format(taxon.taxonkey, i)
                io.save_image(m, fname)

            fname = taxon.taxonkey
            io.save_image(distribution_matrix, fname, enhance=False)
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
        taxa = sesh.query(Taxon).all()[0:args.limit]
    elif args.taxon:
        taxa = sesh.query(Taxon).filter(Taxon.taxonkey.in_(args.taxon)).all()
    else:
        # only select taxa which have a polygon (distribtution table, modelled "TaxaDistribution")
        taxa = sesh.query(Taxon) \
            .join(TaxonDistribution, Taxon.taxonkey == TaxonDistribution.taxon) \
            .all()

    logger.info("Found {} taxa".format(len(taxa)))

    for taxon in taxa:
        if STOP:
            logger.critical("STOP raised")
            break

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
    logger.debug('filter cache usage: {}'.format(filters.filter.BaseFilter.depth_probability.cache_info()))
