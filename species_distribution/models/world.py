""" Taxa data source """

import functools

from sqlalchemy import Column, Integer, Float

from .db import session, SpecDisModel, rows_to_grid


class GridPoint(SpecDisModel):
    __tablename__ = 'world'
    Seq = Column(Integer(), primary_key=True)
    Lon = Column(Float())
    Lat = Column(Float())
    Row = Column(Integer())
    Col = Column(Integer())
    TArea = Column(Float())
    Area = Column(Float())
    PWater = Column(Integer())
    PLand = Column(Integer())
    EleMin = Column(Integer())
    EleMax = Column(Integer())
    EleAvg = Column(Integer())
    Elevation_Min = Column(Integer())
    Elevation_Max = Column(Integer())
    Elevation_Mean = Column(Integer())
    Bathy_Min = Column(Integer())
    Bathy_Max = Column(Integer())
    Bathy_Mean = Column(Integer())
    FAO = Column(Integer())
    LME = Column(Integer())
    BGCP = Column(Integer())
    Distance = Column(Float())
    CoastalProp = Column(Float())
    Shelf = Column(Float())
    Slope = Column(Float())
    Abyssal = Column(Float())
    Estuary = Column(Float())
    Mangrove = Column(Float())
    SeamountSAUP = Column(Float())
    Seamount = Column(Float())
    Coral = Column(Float())
    PProd = Column(Float())
    IceCon = Column(Float())
    SST = Column(Float())
    EEZcount = Column(Float())
    SST2001 = Column(Float())
    BT2001 = Column(Float())
    PP10YrAvg = Column(Float())
    SSTAvg = Column(Float())
    PPAnnual = Column(Float())


class Grid():

    _instance = None
    _lon = None
    _lat = None

    def __new__(cls, *args, **kwargs):
        """ singleton """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self._lon is None:
            self._lon = self.get_grid(field='Lon')

        if self._lat is None:
            self._lat = self.get_grid(field='Lat')

    @property
    def shape(self):
        return self._lon.shape

    @property
    def field_names(self):
        return (c.name for c in GridPoint.__table__.columns)

    @functools.lru_cache(maxsize=2**32)
    def get_grid(self, field='SST'):
        """returns a spatial 2D numpy array of the field specified"""
        attr = getattr(GridPoint, field)

        grid_points = session() \
            .query(GridPoint) \
            .order_by('Row', 'Col') \
            .values(GridPoint.Row, GridPoint.Col, attr)

        return rows_to_grid(grid_points, dtype=attr.type.python_type)

