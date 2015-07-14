""" Taxa data source """

from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table

from .db import SpecDisModel, engine, Base
from ..exceptions import NoPolygonException


def polygon_cells_for_taxon(taxon_key):

    query = """
    WITH dis AS (
        SELECT ST_MAKEVALID(ST_SIMPLIFY(geom,.10)) as geom FROM distribution.taxon_extent
        WHERE taxon_key=%s
    )
    SELECT g.row-1, g.col-1
        FROM distribution.grid g
         JOIN dis d ON (1=1)
        WHERE ST_INTERSECTS(g.geom, d.geom)

    """

    with engine.connect() as conn:
        result = conn.execute(query, taxon_key)
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
        autoload_with=engine
    )

    def __str__(self):
        return str(self.taxonkey)

    @property
    def pelagic(self):
        return self.sppgroup or 3


class TaxonExtent(SpecDisModel):
    __table__ = Table(
        'taxon_extent',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine,
        schema='distribution'
    )


class TaxonHabitat(SpecDisModel):
    __table__ = Table(
        'taxon_habitat',
        Base.metadata,
        Column('taxon_key', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine,
        schema='distribution'
    )

    @property
    def faos(self):
        """returns a list of FAO regions this taxon is found in"""

        # remove nulls
        return [fao for fao in self.found_in_fao_area_id if fao]
