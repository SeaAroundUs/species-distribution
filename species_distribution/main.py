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

logging.basicConfig(format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', level=logging.DEBUG)


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


def create_taxon_distribution(taxon, season_flag=False, season=None):
    if not (taxon.min_depth or taxon.max_depth):
        raise Exception("missing min or max depth")
    if taxon.min_depth <= 1 and taxon.max_depth > -9999:
        flgFromShore = True
    else:
        flgFromShore = False
        # triDist.SetupDistribution(1, -taxaPara.Rows(0).Item("MaxDepth") - 0.01, -taxaPara.Rows(0).Item("MinDepth") + 0.01, 2)
    if taxon.pelagic: # 'SeasonFlg'
        if season == 0:
            lat_north = taxon.LatNorth
            lat_south = taxon.LatSouth
def main():
    logging.info("starting species_distribution")

    args = parse_args()
    distribution = create_output_file(force=args.force)
    grid = Grid()
    taxa = session().query(Taxon)
    logging.info("Found {} taxa".format(taxa.count()))

    for taxon in taxa:
        dataset = distribution.create_dataset(str(taxon.key), grid.shape)

        habitat = session().query.get(taxon.key)

        logging.info("processing taxon: {}, habitat: {}".format(taxon, habitat))

        # get pelagic flag from "SELECT SppGroup FROM TaxonDist WHERE TaxonKey = " & SppKey // if True if 1, else false
        createTaxonDistribution(taxon)
        # seasonal distribution (overloaded createTaxaDistribution)

