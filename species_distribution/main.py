""" Main module for running species_distribution """

import logging
from multiprocessing import Pool
import signal
import sys


import species_distribution.distribution as distribution
import species_distribution.io as io
from species_distribution.models.db import Session
from species_distribution.models.taxa import Taxon, TaxonDistribution
from species_distribution.models.world import Grid
import species_distribution.filters as filters

STOP = False


def configure_logging(level):
    logging.basicConfig(
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
        level=level)

logger = logging.getLogger(__name__)


def signal_handler(*args):
    global STOP
    if STOP:
        logger.warning("SIGINT caught twice, exiting immediately")
        sys.exit(-1)

    logger.warning("Will exit after handling this taxon. Repeat to exit immediately.")
    STOP = True

signal.signal(signal.SIGINT, signal_handler)


def main(args):
    configure_logging(args.verbose and logging.DEBUG or logging.INFO)
    logger.info("starting distribution")

    with Session() as session:
        # get taxa
        if args.limit:
            taxa = session.query(Taxon).all()[0:args.limit]
        elif args.taxon:
            taxa = session.query(Taxon).filter(Taxon.taxonkey.in_(args.taxon)).all()
        else:
            # only select taxa which have a polygon (distribtution table, modelled "TaxaDistribution")
            taxa = session.query(Taxon) \
                .join(TaxonDistribution, Taxon.taxonkey == TaxonDistribution.taxon) \
                .all()

        logger.info("Found {} taxa".format(len(taxa)))

        taxonkeys = [t.taxonkey for t in taxa]

    with Pool(processes=4) as pool:
        res = []
        for taxonkey in taxonkeys:

            if STOP:
                logger.critical("Quitting early due to SIGINT")
                break

            if not args.force and '/taxa/' + str(taxonkey) in io.completed_taxon():
                logger.info('taxon {} exists in output, skipping it.  Use -f to force'.format(taxonkey))
                continue

            res.append(pool.apply_async(distribution.create_and_save_taxon, (taxonkey,), dict(force=args.force)))

        for r in res:
            r.wait()

    io.close()
    logger.info('distribution complete')
    logger.debug('grid cache usage: {}'.format(Grid().get_grid.cache_info()))
    logger.debug('filter cache usage: {}'.format(filters.filter.BaseFilter.depth_probability.cache_info()))
