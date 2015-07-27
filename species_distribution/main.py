""" Main module for running species_distribution """

import logging
from multiprocessing import Pool
import signal
import sys

import species_distribution.distribution as distribution
import species_distribution.io as io
from species_distribution import settings
from species_distribution.models.db import Session
from species_distribution.models.taxa import Taxon, TaxonExtent

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
            taxa = session.query(Taxon) \
                .join(TaxonExtent, Taxon.taxon_key == TaxonExtent.taxon_key)[0:arguments.limit]
        elif arguments.taxon:
            taxa = session.query(Taxon).filter(Taxon.taxon_key.in_(arguments.taxon)).all()
        else:
            # only select taxa which have a polygon (distribution table, modelled "TaxaDistribution")
            taxa = session.query(Taxon) \
                .join(TaxonExtent, Taxon.taxon_key == TaxonExtent.taxon_key) \
                .order_by(Taxon.taxon_key) \
                .all()

        if not arguments.force:
            # running in non-force mode, don't overwrite existing distributions
            completed_taxa = filter(lambda t: t.taxon_key in io.completed_taxon(), taxa)
            taxa = list(filter(lambda t: t.taxon_key not in io.completed_taxon(), taxa))
            for taxon in completed_taxa:
                logger.info('taxon {} exists in output, skipping it.  Use -f to force'.format(taxon.taxon_key))

        logger.info("Found {} taxa".format(len(taxa)))

        taxonkeys = [t.taxon_key for t in taxa]

    with Pool(processes=arguments.processes) as pool:
        res = []
        for taxonkey in taxonkeys:

            if STOP:
                logger.critical("Quitting early due to SIGINT")
                break

            function = distribution.threaded_create_taxon_distribution
            args = (taxonkey,)
            res.append(pool.apply_async(function, args))

        for r in res:
            r.wait()
            taxon_key, matrix = r.get()
            if matrix is not None:
                logger.info('saving {} to DB'.format(taxon_key))
                io.save_database(matrix, taxon_key)

    logger.info('distribution complete')
