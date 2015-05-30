""" Main module for running species_distribution """

from enum import Enum

import os
import sys

import logging

import h5py
import numpy as np

import settings
import species_distribution.exceptions as exceptions
import species_distribution.io as io
from species_distribution.models.db import session
from species_distribution.models.taxa import TaxonPara, TaxonHabitat
from species_distribution.models.world import Grid
import species_distribution.filters as filters


logging.basicConfig(
    format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_output_file(force=False):

    if os.path.isfile(settings.DISTRIBUTION_FILE):
        if force or input("Found distribution file, overwrite it? ").strip().lower().startswith('y'):
            os.unlink(settings.DISTRIBUTION_FILE)
        else:
            logger.critical("Refusing to overwrite existing file")
            sys.exit(-1)

    f = h5py.File(settings.DISTRIBUTION_FILE, 'w')
    f.create_dataset('species_distribution', (360,720))
    return f


class Season(Enum):
    ANNUAL = 0
    SUMMER = 1
    WINTER = 2

class TriangleDistribution():
    def __init__(self):
        self.a1 = {}
        self.b1 = {}
        self.a2 = {}
        self.b2 = {}
        self.MinValue = {}
        self.Part = {}

    def SetupDistribution(self, dist_number, minv, maxv, opt, latskew=0.5):
        self.MinValue[dist_number] = minv
        Range = maxv - minv
        if opt == 1:
            Part1 = Range / 2.0
        elif opt == 2:
            Part1 = Range / 3.0
        elif opt == 3:
            if maxv <= 0.01 and minv <= -0.01:
                Part1 = abs(max(maxv, minv)) + abs((maxv - minv) * (1 - abs(latskew)))
            elif maxv >= 0.01 and minv >= -0.01:
                Part1 = (maxv - minv) * (1 - abs(latskew)) + min(maxv, minv)
        self.Part[dist_number] = Part1

def trapezoid(x, a, b, c, d):
    """Function for a trapezoid density function"""

    if x <= a:
        temp = 0

    if x > a and x < b:
        temp = (x - a) / (b - a)

    if x >= b and x < c:
        temp = 1

    if x >= c and x < d:
        temp = (d - x) / (d - c)

    if x >= d:
        temp = 0

    return temp

def create_taxon_distribution(taxon, habitat, season=Season.ANNUAL):
    """returns a distribution matrix for given taxon taxon by applying filters"""

    polygon_probability_matrix = filters.polygon.filter(taxon)
    fao_probability_matrix = filters.fao.filter(taxon)
    latitude_probability_matrix = filters.latitude.filter(taxon, habitat)

    distribution_matrix = polygon_probability_matrix * \
        fao_probability_matrix * \
        latitude_probability_matrix

    return distribution_matrix

def main(args):
    logger.info("starting distribution")
    sesh = session()
    distribution_file = create_output_file(force=args.force)
    grid = Grid()
    if args.limit:
        taxa = sesh.query(TaxonPara).all()[0:args.limit]
    elif args.taxon:
        taxa = sesh.query(TaxonPara).filter_by(taxonkey=args.taxon).all()
    else:
        taxa = sesh.query(TaxonPara).all()

    logger.info("Found {} taxa".format(len(taxa)))

    for taxon in taxa:

        logger.info("working on taxon {}".format(taxon.taxonkey))

        habitat = sesh.query(TaxonHabitat).get(taxon.taxonkey)

        try:
            distribution = create_taxon_distribution(taxon, habitat, season=Season.ANNUAL)
            _dataset = distribution_file.create_dataset(str(taxon.taxonkey), data=distribution)
        except exceptions.InvalidTaxonException as e:
            logger.warn("Invalid taxon {}. Error: {}".format(taxon, str(e)))
        except exceptions.NoPolygonException as e:
            logger.warn("No polygon exists for taxon {}".format(taxon))

    distribution_file.close()
    logger.info('distribution complete')
