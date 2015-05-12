""" DB data source """

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

Base = declarative_base()

connection_str = 'postgresql://{username}:{password}@{host}:{port}/{db}'.format(**settings.DB)
engine = create_engine(connection_str, echo=True)

# Base.metadata.schema = 'species_distribution'


def session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


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
