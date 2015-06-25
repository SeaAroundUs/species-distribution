""" World data source """

import functools

import numpy as np
from pyproj import Geod
from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table

from .db import engine, session, SpecDisModel, Base


class GridPoint(SpecDisModel):
    __table__ = Table(
        'world',
        Base.metadata,
        Column('Seq', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine
    )


class Grid():

    _instance = None
    longitude = None
    latitude = None

    def __new__(cls, *args, **kwargs):
        """ singleton """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):

        self.shape = (360, 720)

        if self.longitude is None:
            self.longitude = self.get_grid(field='Lon')

        if self.latitude is None:
            self.latitude = self.get_grid(field='Lat')

        assert(self.shape == self.longitude.shape)

    def index_to_seq(self, index):
        """ given an (x,y) index to the grid, return seq number """
        y, x = index
        h, w = self.shape
        return (x + w * y) + 1

    @property
    @functools.lru_cache()
    def cell_height(self):
        cell_height = np.full(self.shape, np.nan)
        geod = Geod(ellps='WGS84')
        for i in range(self.shape[0]):
            _az12, _az21, cell_length = geod.inv(
                self.longitude[i, 0],
                self.latitude[i, 0] + .25,
                self.longitude[i, 0],
                self.latitude[i, 0] - .25,
            )
            cell_height[i, :] = cell_length

        return cell_height

    @property
    @functools.lru_cache(maxsize=2**32)
    def area_coast(self):
        coastal_prop = self.get_grid('CoastalProp')
        water_area = self.get_grid('Area')  # Area <-> WaterArea
        return coastal_prop * water_area

    @property
    @functools.lru_cache(maxsize=2**32)
    def area_offshore(self):
        coastal_prop = self.get_grid('CoastalProp')
        water_area = self.get_grid('Area')  # Area <-> WaterArea
        return (1 - coastal_prop) * water_area

    @property
    def field_names(self):
        return (c.name for c in GridPoint.__table__.columns)

    def rows_to_grid(self, rows, dtype=np.float):
        """ convert ordered rows of (value) to a 2d grid """
        grid = np.fromiter(rows, dtype=dtype)
        return grid.reshape(self.shape)

    @functools.lru_cache(maxsize=2 ** 32)
    def get_grid(self, field='SST'):
        """returns a spatial 2D numpy array of the field specified"""

        attr = getattr(GridPoint, field)

        query = session() \
            .query(GridPoint) \
            .order_by('Row', 'Col') \
            .values(attr)

        grid_points = (r[0] for r in query)

        return self.rows_to_grid(grid_points, dtype=attr.type.python_type)
