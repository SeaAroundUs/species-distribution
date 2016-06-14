""" Main module for running species_distribution """

import logging
from multiprocessing import Pool
import signal
import sys

import species_distribution.distribution as distribution
from species_distribution import sd_io as io
from species_distribution.models.db import Session
from species_distribution.models.taxa import Taxon, TaxonExtent, TaxonHabitat
from species_distribution import settings
from sqlalchemy import exists, and_
import numpy as np

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
    logger.info("connecting to Host: {} DB: {} User: {}".format(
            settings.DB['host'],
            settings.DB['db'],
            settings.DB['username'])
    )

    taxonkeys = []
    with Session() as session:
        # get taxa
        if arguments.limit:
            taxa = session.query(Taxon) \
                .filter(Taxon.is_retired == False)\
                .filter(exists().where(Taxon.taxon_key == TaxonExtent.taxon_key)) \
                .filter(exists().where(
                        and_(Taxon.taxon_key == TaxonHabitat.taxon_key, TaxonHabitat.found_in_fao_area_id.isnot(None))
                    )
                ) \
                [0:arguments.limit]

        elif arguments.taxon:
            taxa = session.query(Taxon) \
                .filter(Taxon.taxon_key.in_(arguments.taxon))\
                .filter(Taxon.is_retired == False)\
                .filter(exists().where(Taxon.taxon_key == TaxonExtent.taxon_key)) \
                .filter(exists().where(
                        and_(Taxon.taxon_key == TaxonHabitat.taxon_key, TaxonHabitat.found_in_fao_area_id.isnot(None))
                    )
                ) \
                .all()
        else:
            # only select taxa which have a polygon and habitat (distribution table, modelled "TaxaDistribution")
            taxa = session.query(Taxon)\
                .filter(Taxon.is_retired == False)\
                .filter(exists().where(Taxon.taxon_key == TaxonExtent.taxon_key)) \
                .filter(exists().where(
                        and_(Taxon.taxon_key == TaxonHabitat.taxon_key, TaxonHabitat.found_in_fao_area_id.isnot(None))
                    )
                ) \
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

    num_of_taxons_to_process = len(taxonkeys)

    if num_of_taxons_to_process == 0:
        logger.info("No taxons selected for processing, process aborted.")
        return

    if arguments.processes > num_of_taxons_to_process:
        arguments.processes = num_of_taxons_to_process

    if arguments.numpy_exception:
        np.seterr(all='raise')

    if arguments.processes == 1:
        # no pool
        for i, taxon_key in enumerate(taxonkeys):
            if STOP:
                logger.critical("Quitting early due to SIGINT")
                break

            logger.info("starting work on taxon key {} [{}/{}]".format(taxon_key, i + 1, len(taxa)))
            _, matrix = distribution.create_taxon_distribution(taxon_key)
            distribution.save_database(taxon_key, matrix)

    else:
        # pool
        with Pool(processes=arguments.processes) as pool:
            res = []
            for taxonkey in taxonkeys:

                if STOP:
                    logger.critical("Quitting early due to SIGINT")
                    break

                function = distribution.create_taxon_distribution
                args = (taxonkey,)
                res.append(pool.apply_async(function, args))

            for r in res:
                taxon_key, matrix = r.get()
                distribution.save_database(taxon_key, matrix)


    logger.info('distribution complete')
