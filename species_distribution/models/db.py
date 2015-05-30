""" DB data source """

import itertools
import operator

import numpy as np
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

Base = declarative_base()

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)
engine = create_engine(connection_str, echo=False)

# Base.metadata.schema = 'species_distribution'


def session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def create_grid():

    conn = session().connection()

    grid_distribution_intersection_query = """
    SELECT seq, row, col from grid where geom && (select geom from distribution where taxon=100036 );
    """
    conn.execute(grid_distribution_intersection_query)


def rows_to_grid(rows, dtype=np.float):
    # convert ordered rows of (row,col,value) to a 2d grid
    _grid = []
    for _, row in itertools.groupby(rows, key=operator.itemgetter(0)):
        _grid.append([x[2] for x in row])

    return np.array(_grid, dtype=dtype)


class SpecDisModel(Base):
    __abstract__ = True


if __name__ == "__main__":
    # attempt automap
    from sqlalchemy.ext.automap import automap_base
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    TaxonNom = Base.classes.TaxonNom

    import logging
    logging.warn(session().query(TaxonNom).all())
