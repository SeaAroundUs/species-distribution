""" World data source """

import functools

import logging
from multiprocessing import Pool
import signal
import sys
import species_distribution.distribution as distribution
from species_distribution import sd_io as io
from species_distribution.models.taxa import Taxon, TaxonExtent, TaxonHabitat
from species_distribution import settings
from sqlalchemy import exists, and_
import numpy as np
from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table
from sqlalchemy import exists, and_
from .db import SpecDisModel, Base




class ValidationRule(SpecDisModel):
    __table__ = Table(
        'validation_rule',
        Base.metadata,
        Column('rule_id', Integer(), primary_key=True),
        autoload=True,
        extend_existing=True
    )



class ValidationResult(SpecDisModel):
    __table__ = Table(
        'validation_result',
        Base.metadata,
        autoload=True,
        extend_existing=True
    )




