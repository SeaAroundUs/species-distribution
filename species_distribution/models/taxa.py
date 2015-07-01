""" Taxa data source """

from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table

from .db import SpecDisModel, engine, Base
from species_distribution import exceptions


FAO_IDS = (18, 21, 27, 31, 34, 37, 41, 47, 48, 51, 57, 58, 61, 67, 71, 77, 81, 87, 88)


def polygon_cells_for_taxon(taxon_key):

    query = """
    WITH dis AS (
        SELECT ST_SIMPLIFY(geom,.10) as geom FROM distribution
        WHERE taxon=%s
    )
    SELECT g.row-1, g.col-1
        FROM grid g
         JOIN dis d ON (1=1)
        WHERE ST_INTERSECTS(g.geom, d.geom)

    """

    with engine.connect() as conn:
        result = conn.execute(query, taxon_key)
        data = result.fetchall()
        if len(data) == 0:
            raise exceptions.NoPolygonException
        return data


class Taxon(SpecDisModel):
    __table__ = Table(
        'qryalltaxon',
        Base.metadata,
        Column('taxonkey', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine
    )

    def __str__(self):
        return str(self.taxonkey)

    @property
    def faos(self):
        """returns a list of FAO regions this taxon is found in"""

        return list(filter(lambda id: getattr(self, 'fao' + str(id)) == 1, FAO_IDS))

    @property
    def pelagic(self):
        return self.sppgroup or 3


class TaxonDistribution(SpecDisModel):
    __table__ = Table(
        'distribution',
        Base.metadata,
        Column('taxon', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine
    )


class TaxonHabitat(SpecDisModel):
    __table__ = Table(
        'taxon_habitat',
        Base.metadata,
        Column('TaxonKey', Integer(), primary_key=True),
        autoload=True,
        autoload_with=engine
    )
