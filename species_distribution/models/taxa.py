""" Taxa data source """

import functools

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from .db import SpecDisModel, Session, Base
from ..exceptions import NoPolygonException

@functools.lru_cache(maxsize=None)
def polygon_cells_for_taxon(taxon_key):

    query = """
    WITH dis AS (
        SELECT ST_MAKEVALID(ST_SIMPLIFY(geom,.10)) as geom FROM distribution.taxon_extent
        WHERE taxon_key=:taxon_key
    )
    SELECT g.row-1, g.col-1
        FROM distribution.grid g
         JOIN dis d ON (1=1)
        WHERE ST_INTERSECTS(g.geom, d.geom)

    """

    with Session() as session:
        result = session.execute(query, {'taxon_key': taxon_key})
        data = result.fetchall()
        if len(data) == 0:
            raise NoPolygonException
        return data


class Taxon(SpecDisModel):
    __table__ = Table(
        'taxon',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
    )

    def __str__(self):
        return str(self.taxonkey)

    @property
    def pelagic(self):
        return self.functional_group_id in (1,2,3)


class TaxonDistributionLog(SpecDisModel):
    __table__ = Table(
        'taxon_distribution_log',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
        schema='distribution'
    )

    taxon = relationship('Taxon',
        backref = 'distribution_log',
        primaryjoin = 'Taxon.taxon_key == TaxonDistributionLog.taxon_key',
        foreign_keys='Taxon.taxon_key')

    def __str__(self):
        return str(self.taxonkey)


class TaxonExtent(SpecDisModel):
    __table__ = Table(
        'taxon_extent',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
        schema='distribution'
    )


class TaxonHabitat(SpecDisModel):
    __table__ = Table(
        'taxon_habitat',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
        schema='distribution'
    )

    @property
    def faos(self):
        """returns a list of FAO regions this taxon is found in"""

        # remove nulls
        return [fao for fao in self.found_in_fao_area_id if fao]
