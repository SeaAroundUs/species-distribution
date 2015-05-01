#!/usr/bin/env python

"""creates tables for all models which don't have them already"""

from species_distribution.models.taxa import *
from species_distribution.models.world import *
from species_distribution.models.db import Base, engine

Base.metadata.create_all(engine)
