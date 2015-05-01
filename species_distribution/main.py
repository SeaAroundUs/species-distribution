""" Main module for running species_distribution """

import argparse
import os
import sys

import logging

import h5py

import settings
from species_distribution.models.db import session
from species_distribution.models.taxa import Taxon
from species_distribution.models.world import Grid

logging.basicConfig(format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', level=logging.INFO)


def create_output_file(force=False):

    if os.path.isfile(settings.DISTRIBUTION_FILE):
        if force or input("Found distribution file, overwrite it? ").strip().lower().startswith('y'):
            os.unlink(settings.DISTRIBUTION_FILE)
        else:
            logging.critical("Refusing to overwrite existing file")
            sys.exit(-1)

    f = h5py.File(settings.DISTRIBUTION_FILE, 'w')
    f.create_dataset('species_distribution', (360,720))
    return f


def parse_args():
    parser = argparse.ArgumentParser(description='Species Distribution')
    parser.add_argument('-f', '--force', action='store_true', help='overwrite any existing output file: {}'.format(settings.DISTRIBUTION_FILE))
    return parser.parse_args()


def main():
    logging.info("starting species_distribution")

    args = parse_args()
    distribution = create_output_file(force=args.force)
    grid = Grid()
    taxa = session().query(Taxon)
    logging.info("Found {} taxa".format(taxa.count()))

    for taxon in taxa:
        distribution.create_dataset(str(taxon.key), grid.shape)

        # get pelagic flag from "SELECT SppGroup FROM TaxonDist WHERE TaxonKey = " & SppKey // if True if 1, else false
        # createTaxaDistribution
        # seasonal distribution (overloaded createTaxaDistribution)
