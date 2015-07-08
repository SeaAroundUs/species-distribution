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


def main(arguments):
    configure_logging(arguments.verbose and logging.DEBUG or logging.INFO)
    logger.info("starting distribution")

    with Session() as session:
        # get taxa
        if arguments.limit:
            taxa = session.query(Taxon).all()[0:arguments.limit]
        elif arguments.taxon:
            taxa = session.query(Taxon).filter(Taxon.taxonkey.in_(arguments.taxon)).all()
        else:
            # only select taxa which have a polygon (distribtution table, modelled "TaxaDistribution")
            taxa = session.query(Taxon) \
                .join(TaxonDistribution, Taxon.taxonkey == TaxonDistribution.taxon) \
                .all()

        logger.info("Found {} taxa".format(len(taxa)))

        taxonkeys = [t.taxonkey for t in taxa]

    with Pool(processes=arguments.processes) as pool:
        res = []
        for taxonkey in taxonkeys:

            if STOP:
                logger.critical("Quitting early due to SIGINT")
                break

            if not arguments.force and '/taxa/' + str(taxonkey) in io.completed_taxon():
                logger.info('taxon {} exists in output, skipping it.  Use -f to force'.format(taxonkey))
                continue

            function = distribution.create_and_save_taxon
            args = (taxonkey,)
            kwargs = dict(force=arguments.force)
            if arguments.processes > 1:
                res.append(pool.apply_async(function, args, kwargs))
            else:
                function(*args, **kwargs)

        for r in res:
            r.wait()

    io.close()
    logger.info('distribution complete')
